# packages/crawler/crawl_runner.py
"""Main crawl orchestrator — BFS frontier crawl with sitemap seeding and robots.txt respect."""

import asyncio
from collections import deque
from datetime import datetime, timezone
from typing import Sequence
from urllib.parse import urlparse

from packages.crawler.models import CrawlConfig, CrawlResult, CrawlSummary, PageRecord
from packages.crawler.page_fetcher import PageFetcher
from packages.crawler.robots_parser import RobotParser
from packages.crawler.sitemap_parser import SitemapParser
from packages.shared.logging import get_logger

logger = get_logger(__name__)


class CrawlRunner:
    """Orchestrates a full crawl session: sitemap discovery → BFS page crawl → result.
    
    Usage:
        config = CrawlConfig(start_url="https://example.com", max_pages=50)
        runner = CrawlRunner(config)
        result = await runner.run()
    """

    def __init__(
        self,
        config: CrawlConfig,
        max_concurrent: int = 5,
    ) -> None:
        self.config = config
        self.max_concurrent = max_concurrent

        # Internal state
        self._robot_parser = RobotParser(
            domain=config.domain or "",
            user_agent=config.user_agent,
        )
        self._result: CrawlResult | None = None

    # ── public API ──────────────────────────────────────────────────────────────

    async def run(self) -> CrawlResult:
        """Execute the full crawl and return a CrawlResult."""
        self._result = CrawlResult(
            config=self.config,
            started_at=datetime.now(timezone.utc),
        )
        logger.info(
            "Starting crawl: start_url=%s domain=%s max_pages=%d depth=%d",
            self.config.start_url,
            self.config.domain,
            self.config.max_pages,
            self.config.crawl_depth,
        )

        # Discover seed URLs from sitemap(s)
        seed_urls: list[str] = []
        if self.config.follow_sitemaps:
            sitemap_parser = SitemapParser(
                domain=self.config.domain or "",
                timeout_ms=self.config.timeout_ms,
            )
            seed_urls = await sitemap_parser.discover_and_parse()

        # Always add the start URL as a seed if sitemap found nothing
        if not seed_urls:
            seed_urls.append(str(self.config.start_url))

        logger.info("Discovered %d seed URLs from sitemap", len(seed_urls))

        # BFS crawl
        await self._crawl_bfs(seed_urls)

        self._result.completed_at = datetime.now(timezone.utc)
        logger.info(
            "Crawl complete: discovered=%d crawled=%d duration=%.1fs",
            self._result.pages_discovered,
            self._result.pages_crawled,
            self._result.duration_seconds,
        )
        return self._result

    def summary(self) -> CrawlSummary:
        """Return a CrawlSummary from the last run."""
        if self._result is None:
            raise RuntimeError("run() must be called before summary()")

        pages = self._result.pages
        blocked = sum(1 for p in pages if p.is_robots_blocked)
        non_indexable = sum(1 for p in pages if not p.is_indexable)
        with_schema = sum(1 for p in pages if p.has_schema)
        word_counts = [p.word_count for p in pages if p.word_count is not None]
        avg_wc = sum(word_counts) / len(word_counts) if word_counts else None

        return CrawlSummary(
            pages_discovered=self._result.pages_discovered,
            pages_crawled=self._result.pages_crawled,
            crawl_duration_seconds=self._result.duration_seconds,
            error_count=sum(1 for p in pages if p.status_code is None),
            blocked_by_robots_count=blocked,
            non_indexable_count=non_indexable,
            pages_with_schema_count=with_schema,
            average_word_count=avg_wc,
        )

    # ── BFS crawl ───────────────────────────────────────────────────────────────

    async def _crawl_bfs(self, seed_urls: Sequence[str]) -> None:
        """Breadth-first crawl from seed URLs, respecting max_pages and crawl_depth."""

        if self._result is None:
            raise RuntimeError("_result must be initialized before calling _crawl_bfs")

        # frontier: deque of (url, depth, parent_url)
        frontier: deque[tuple[str, int, str | None]] = deque()
        seen_urls: set[str] = set()

        # Normalize seed URLs and add to frontier
        for url in seed_urls:
            normalized = self._normalize_url(url)
            if normalized and normalized not in seen_urls:
                seen_urls.add(normalized)
                frontier.append((normalized, 0, None))

        # Seed the start_url too if it wasn't in sitemaps
        start_str = str(self.config.start_url)
        if start_str not in seen_urls:
            seen_urls.add(start_str)
            frontier.append((start_str, 0, None))

        async with PageFetcher(self.config, robot_parser=self._robot_parser) as fetcher:
            while frontier and len(self._result.pages) < self.config.max_pages:
                # Batch size = min(frontier size, max_concurrent)
                batch: list[tuple[str, int, str | None]] = []
                while frontier and len(batch) < self.max_concurrent:
                    batch.append(frontier.popleft())

                records = await fetcher.fetch_pages(
                    [url for url, _, _ in batch],
                    parent_url=batch[0][2] if len(batch) == 1 else None,
                )

                for (url, depth, parent_url), record in zip(batch, records):
                    self._result.pages_discovered += 1

                    if isinstance(record, Exception):
                        logger.warning("Error fetching %s: %s", url, record)
                        continue
                    if record.status_code is None and not record.is_robots_blocked:
                        logger.warning("No response for %s", url)
                        continue

                    # Adjust crawl_depth on the record
                    record.crawl_depth = depth
                    record.parent_page_url = parent_url

                    self._result.pages.append(record)
                    if record.status_code is not None:
                        self._result.pages_crawled += 1

                    # Enqueue discovered outbound URLs up to depth limit
                    if depth < self.config.crawl_depth:
                        for next_url in record.outbound_urls:
                            next_normalized = self._normalize_url(next_url)
                            if (
                                next_normalized
                                and next_normalized not in seen_urls
                                and self._is_same_domain(next_normalized)
                            ):
                                seen_urls.add(next_normalized)
                                frontier.append((next_normalized, depth + 1, url))

                logger.debug(
                    "Frontier batch done: total_seen=%d total_crawled=%d frontier_remaining=%d",
                    len(seen_urls),
                    self._result.pages_crawled,
                    len(frontier),
                )

    # ── helpers ─────────────────────────────────────────────────────────────────

    def _normalize_url(self, url: str) -> str | None:
        """Normalize a URL: strip trailing slash, lowercase scheme, remove fragment."""
        try:
            parsed = urlparse(url)
            # Remove fragment
            return f"{parsed.scheme}://{parsed.netloc}{parsed.path}".rstrip("/")
        except Exception:
            return None

    def _is_same_domain(self, url: str) -> bool:
        """Return True if URL belongs to the configured crawl domain."""
        domain = self.config.domain
        if not domain:
            return True
        parsed = urlparse(url)
        return parsed.netloc == domain
