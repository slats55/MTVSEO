# packages/crawler/crawl_worker.py
"""Standalone crawl worker script and optional Celery task.

Usage (standalone):
    python -m packages.crawler.crawl_worker https://example.com

Usage (Celery — when Celery is configured):
    from packages.crawler.crawl_worker import crawl_website_task
    crawl_website_task.delay(crawl_run_id="...", start_url="https://example.com", ...)

The worker:
1. Creates a CrawlRunner and executes the crawl
2. Upserts Page records into the DB (matched by url + crawl_run_id)
3. Updates CrawlRun with pages_discovered, pages_crawled, started_at, completed_at, status
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from datetime import datetime, timezone
from uuid import UUID

# Add project root to path for standalone invocation
sys.path.insert(0, str(__file__).rsplit("/packages/", 1)[0])

from packages.crawler.crawl_runner import CrawlRunner
from packages.crawler.models import CrawlConfig, CrawlSummary
from packages.shared.config import (
    DEFAULT_CRAWL_DEPTH,
    DEFAULT_CRAWL_DELAY_MS,
    DEFAULT_MAX_PAGES,
    DEFAULT_USER_AGENT,
)
from packages.shared.logging import get_logger

logger = get_logger(__name__)


# ── Celery task (only registered when Celery is available) ───────────────────

_celerity_available = False
try:
    from celery import shared_task  # type: ignore

    _celerity_available = True
except ImportError:
    def _dummy_task(**_kwargs):  # type: ignore
        """Placeholder when Celery is not installed."""
        raise ImportError("Celery is not installed. Install with: pip install celery")

    shared_task = _dummy_task


def _update_crawl_run_db(
    crawl_run_id: UUID,
    status: str,
    started_at: datetime,
    completed_at: datetime | None = None,
    pages_discovered: int = 0,
    pages_crawled: int = 0,
    error_message: str | None = None,
) -> None:
    """Update a CrawlRun DB record by ID. Only runs when DB is available."""
    try:
        from services.api.database import async_session_maker
        from services.api.models.crawl_run import CrawlRun
        from services.api.models.enums import CrawlStatus
        import uuid

        async def _update() -> None:
            async with async_session_maker() as session:
                from sqlalchemy import select, update
                stmt = (
                    update(CrawlRun)
                    .where(CrawlRun.id == crawl_run_id)
                    .values(
                        status=CrawlStatus(status),
                        started_at=started_at,
                        completed_at=completed_at,
                        pages_discovered=pages_discovered,
                        pages_crawled=pages_crawled,
                        error_message=error_message,
                    )
                )
                await session.execute(stmt)
                await session.commit()

        asyncio.run(_update())
    except Exception as exc:
        logger.warning("Could not update CrawlRun %s in DB: %s", crawl_run_id, exc)


def _upsert_pages_db(crawl_run_id: UUID, summary: CrawlSummary, pages: list, config: CrawlConfig) -> None:
    """Upsert Page records into DB. Skipped when DB is not available."""
    try:
        from services.api.database import async_session_maker
        from services.api.models.page import Page
        from uuid import UUID

        async def _upsert() -> None:
            async with async_session_maker() as session:
                for record in pages:
                    canonical = (
                        record.canonical_url
                        if record.canonical_url
                        else None
                    )
                    stmt = Page(
                        crawl_run_id=crawl_run_id,
                        url=record.url,
                        canonical_url=canonical,
                        status_code=record.status_code,
                        title=record.title,
                        meta_description=record.meta_description,
                        h1=record.h1,
                        h2_headings=record.h2_headings,
                        word_count=record.word_count,
                        internal_links_count=record.internal_links_count,
                        external_links_count=record.external_links_count,
                        images_count=record.images_count,
                        images_without_alt=record.images_without_alt,
                        has_schema=record.has_schema,
                        schema_types=record.schema_types,
                        is_indexable=record.is_indexable,
                        is_canonical=record.is_canonical,
                        is_robots_blocked=record.is_robots_blocked,
                        crawl_depth=record.crawl_depth,
                        redirect_url=record.redirect_url,
                    )
                    session.add(stmt)
                await session.commit()

        asyncio.run(_upsert())
    except Exception as exc:
        logger.warning("Could not upsert Page records for crawl_run %s: %s", crawl_run_id, exc)


# ── Celery task ────────────────────────────────────────────────────────────────

if _celerity_available:

    @shared_task(bind=True, max_retries=3)
    def crawl_website_task(
        self,
        crawl_run_id: str,
        start_url: str,
        max_pages: int = DEFAULT_MAX_PAGES,
        crawl_depth: int = DEFAULT_CRAWL_DEPTH,
        delay_ms: int = DEFAULT_CRAWL_DELAY_MS,
        user_agent: str = DEFAULT_USER_AGENT,
        respect_robots: bool = True,
        follow_sitemaps: bool = True,
    ) -> dict:
        """Celery task: crawl a website and store results in the DB.

        Args:
            crawl_run_id: UUID of the CrawlRun record to update
            start_url: URL to start crawling from
            max_pages: max pages to crawl (default from config)
            crawl_depth: max link depth to follow (default from config)
            delay_ms: milliseconds between requests (default from config)
            user_agent: user-agent string to use
            respect_robots: whether to obey robots.txt
            follow_sitemaps: whether to discover URLs from sitemap.xml first

        Returns:
            dict with pages_discovered, pages_crawled, duration_seconds, success
        """
        import asyncio

        async def _run() -> dict:
            config = CrawlConfig(
                start_url=start_url,
                max_pages=max_pages,
                crawl_depth=crawl_depth,
                delay_ms=delay_ms,
                user_agent=user_agent,
                respect_robots=respect_robots,
                follow_sitemaps=follow_sitemaps,
            )
            runner = CrawlRunner(config)
            result = await runner.run()
            summary = runner.summary()

            # Update CrawlRun in DB
            _update_crawl_run_db(
                crawl_run_id=UUID(crawl_run_id),
                status="COMPLETED" if result.success else "FAILED",
                started_at=result.started_at,
                completed_at=result.completed_at,
                pages_discovered=result.pages_discovered,
                pages_crawled=result.pages_crawled,
                error_message=result.error_message,
            )

            # Upsert pages
            _upsert_pages_db(UUID(crawl_run_id), summary, result.pages, config)

            return {
                "crawl_run_id": crawl_run_id,
                "pages_discovered": result.pages_discovered,
                "pages_crawled": result.pages_crawled,
                "duration_seconds": result.duration_seconds,
                "success": result.success,
                "error_message": result.error_message,
            }

        return asyncio.run(_run())


# ── Standalone entry point ─────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="SEO Agent OS — standalone crawl worker")
    parser.add_argument("start_url", help="URL to start crawling from")
    parser.add_argument("--max-pages", type=int, default=DEFAULT_MAX_PAGES)
    parser.add_argument("--depth", type=int, default=DEFAULT_CRAWL_DEPTH)
    parser.add_argument("--delay-ms", type=int, default=DEFAULT_CRAWL_DELAY_MS)
    parser.add_argument("--user-agent", type=str, default=DEFAULT_USER_AGENT)
    parser.add_argument("--no-robots", action="store_true", help="Ignore robots.txt")
    parser.add_argument("--no-sitemap", action="store_true", help="Skip sitemap discovery")
    parser.add_argument("--crawl-run-id", type=str, default=None, help="CrawlRun UUID to update in DB")
    args = parser.parse_args()

    config = CrawlConfig(
        start_url=args.start_url,
        max_pages=args.max_pages,
        crawl_depth=args.depth,
        delay_ms=args.delay_ms,
        user_agent=args.user_agent,
        respect_robots=not args.no_robots,
        follow_sitemaps=not args.no_sitemap,
    )

    async def _run() -> None:
        runner = CrawlRunner(config)
        result = await runner.run()
        summary = runner.summary()

        print("\n=== Crawl Result ===")
        print(f"  Start URL:  {config.start_url}")
        print(f"  Domain:     {config.domain}")
        print(f"  Discovered: {result.pages_discovered}")
        print(f"  Crawled:   {result.pages_crawled}")
        print(f"  Duration:  {result.duration_seconds:.1f}s")
        print(f"  Success:   {result.success}")
        print(f"\n=== Summary ===")
        print(f"  Blocked by robots: {summary.blocked_by_robots_count}")
        print(f"  Non-indexable:     {summary.non_indexable_count}")
        print(f"  Pages with schema: {summary.pages_with_schema_count}")
        print(f"  Avg word count:    {summary.average_word_count:.0f}" if summary.average_word_count else "  Avg word count:    N/A")

        if result.pages:
            print(f"\n=== Sample URLs (first 10) ===")
            for p in result.pages[:10]:
                print(f"  [{p.status_code or 'ERR'}] {p.url[:80]}")

        # Update DB if crawl_run_id provided
        if args.crawl_run_id:
            run_uuid = UUID(args.crawl_run_id)
            _update_crawl_run_db(
                crawl_run_id=run_uuid,
                status="COMPLETED" if result.success else "FAILED",
                started_at=result.started_at,
                completed_at=result.completed_at,
                pages_discovered=result.pages_discovered,
                pages_crawled=result.pages_crawled,
                error_message=result.error_message,
            )
            _upsert_pages_db(run_uuid, summary, result.pages, config)
            print(f"\nDB updated for CrawlRun {args.crawl_run_id}")

    asyncio.run(_run())


if __name__ == "__main__":
    main()
