# packages/crawler/page_fetcher.py
"""Async HTTP fetching with rate limiting, robots.txt enforcement, and HTML parsing."""

import asyncio
import re
import time
from datetime import datetime, timezone
from typing import Sequence
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup

from .models import CrawlConfig, PageRecord
from .robots_parser import RobotParser
from ..shared.shared_logger import get_logger

logger = get_logger(__name__)

# Reusable content-type patterns that indicate HTML (no point crawling PDFs, images, etc.)
HTML_CONTENT_PATTERNS = re.compile(
    r"^(text/html|application/xhtml\+xml|application/xml)(?:;|$)",
    re.IGNORECASE,
)


class PageFetcher:
    """Async page fetcher with per-domain rate limiting and robots.txt enforcement.
    
    Designed to be shared across a crawl session. Use fetch_page() for individual
    pages; use fetch_pages() for bulk fetching with automatic concurrency control.
    """

    def __init__(
        self,
        config: CrawlConfig,
        robot_parser: RobotParser | None = None,
        max_concurrent: int = 5,
    ) -> None:
        self.config = config
        self.robot_parser = robot_parser or RobotParser(
            domain=config.domain or "",
            user_agent=config.user_agent,
        )
        self.max_concurrent = max_concurrent
        # Semaphore limits concurrent connections per domain
        self._semaphore: asyncio.Semaphore | None = None
        # Last-request timestamp for inter-request delay enforcement
        self._last_request_time: float = 0.0
        self._delay_lock = asyncio.Lock()
        self._client: httpx.AsyncClient | None = None

    # ── public API ──────────────────────────────────────────────────────────────

    async def __aenter__(self) -> "PageFetcher":
        await self.robot_parser.ensure_fetched()
        self._client = httpx.AsyncClient(
            timeout=httpx.Timeout(self.config.timeout_ms / 1000),
            follow_redirects=True,
            headers={"User-Agent": self.config.user_agent},
            limits=httpx.Limits(
                max_connections=self.max_concurrent,
                max_keepalive_connections=self.max_concurrent,
            ),
        )
        self._semaphore = asyncio.Semaphore(self.max_concurrent)
        return self

    async def __aexit__(self, *_: object) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None
        self._semaphore = None

    async def fetch_page(self, url: str, parent_url: str | None = None) -> PageRecord:
        """Fetch and parse a single URL, returning a PageRecord.
        
        Returns a PageRecord with is_robots_blocked=True if robots.txt blocks it.
        """
        # robots.txt check first
        if self.config.respect_robots and not self.robot_parser.can_fetch(url):
            logger.debug("Blocked by robots.txt: %s", url)
            return PageRecord(
                url=url,
                is_robots_blocked=True,
                crawl_depth=0,
                parent_page_url=parent_url,
            )

        # Rate limit: enforce delay between requests
        await self._enforce_delay()

        try:
            response = await self._fetch(url)
        except Exception as exc:
            logger.warning("Failed to fetch %s: %s", url, exc)
            return PageRecord(
                url=url,
                parent_page_url=parent_url,
                crawl_depth=0,
            )

        content_type = response.headers.get("content-type", "")
        if not HTML_CONTENT_PATTERNS.match(content_type):
            logger.debug("Skipping non-HTML content-type %s for %s", content_type, url)
            return PageRecord(
                url=url,
                status_code=response.status_code,
                parent_page_url=parent_url,
                crawl_depth=0,
            )

        return self._parse_html(
            html=response.text,
            url=str(response.url),
            status_code=response.status_code,
            parent_url=parent_url,
        )

    async def fetch_pages(self, urls: Sequence[str], parent_url: str | None = None) -> list[PageRecord]:
        """Fetch multiple URLs concurrently, respecting max_concurrent limit."""
        tasks = [self.fetch_page(url, parent_url=parent_url) for url in urls]
        return await asyncio.gather(*tasks, return_exceptions=True)  # type: ignore[return-value]

    # ── internal helpers ─────────────────────────────────────────────────────────

    async def _fetch(self, url: str) -> httpx.Response:
        """Make the HTTP request with concurrency gating."""
        if self._semaphore is None:
            raise RuntimeError("PageFetcher must be used as async context manager")
        async with self._semaphore:
            if self._client is None:
                raise RuntimeError("HTTP client not initialized")
            return await self._client.get(url)

    async def _enforce_delay(self) -> None:
        """Ensure at least config.delay_seconds pass between consecutive requests."""
        async with self._delay_lock:
            now = time.monotonic()
            elapsed = now - self._last_request_time
            if elapsed < self.config.delay_seconds:
                await asyncio.sleep(self.config.delay_seconds - elapsed)
            self._last_request_time = time.monotonic()

    def _parse_html(
        self,
        html: str,
        url: str,
        status_code: int,
        parent_url: str | None,
    ) -> PageRecord:
        """Parse HTML with BeautifulSoup, extracting all relevant fields."""
        soup = BeautifulSoup(html, "lxml")

        # Canonical URL
        canonical = self._extract_canonical(soup, url)

        # robots noindex check (meta robots tag)
        is_indexable = self._extract_is_indexable(soup)

        # Title
        title = None
        title_tag = soup.find("title")
        if title_tag and title_tag.string:
            title = title_tag.string.strip()

        # Meta description
        meta_desc = None
        meta_tag = soup.find("meta", attrs={"name": "description"})
        if meta_tag and meta_tag.get("content"):
            meta_desc = meta_tag["content"].strip()

        # H1
        h1 = None
        h1_tag = soup.find("h1")
        if h1_tag and h1_tag.string:
            h1 = h1_tag.string.strip()

        # H2 headings (all of them)
        h2_headings = [h.get_text(strip=True) for h in soup.find_all("h2") if h.string]

        # Word count (text content only, stripped)
        body = soup.find("body")
        word_count = None
        if body:
            text = body.get_text(separator=" ", strip=True)
            word_count = len(text.split())

        # Links (internal vs external)
        internal_links: list[str] = []
        external_links: list[str] = []
        domain = self.config.domain or urlparse(url).netloc

        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"]
            if not href or href.startswith(("#", "javascript:", "mailto:", "tel:")):
                continue
            absolute = urljoin(url, href)
            parsed = urlparse(absolute)
            if parsed.netloc == domain:
                internal_links.append(absolute)
            else:
                external_links.append(absolute)

        # Images
        images = soup.find_all("img")
        images_without_alt = [img for img in images if not img.get("alt", "").strip()]
        images_count = len(images)

        # Schema.org structured data
        schema_types: list[str] = []
        has_schema = False
        for script in soup.find_all("script", type="application/ld+json"):
            try:
                import json
                data = json.loads(script.string or "")
                items = data if isinstance(data, list) else [data]
                for item in items:
                    if "@type" in item:
                        t = item["@type"]
                        schema_types.extend(t if isinstance(t, list) else [t])
            except Exception:
                pass
        has_schema = len(schema_types) > 0

        # Determine canonical vs current URL
        is_canonical = canonical is None or canonical == url

        return PageRecord(
            url=url,
            canonical_url=canonical,
            status_code=status_code,
            title=title,
            meta_description=meta_desc,
            h1=h1,
            h2_headings=h2_headings,
            word_count=word_count,
            internal_links_count=len(internal_links),
            external_links_count=len(external_links),
            images_count=images_count,
            images_without_alt=len(images_without_alt),
            has_schema=has_schema,
            schema_types=list(set(schema_types)),
            is_indexable=is_indexable,
            is_canonical=is_canonical,
            is_robots_blocked=False,
            crawl_depth=0,
            parent_page_url=parent_url,
            redirect_url=None,
            raw_html=html[:100_000],  # cap at 100 KB for storage
            fetched_at=datetime.now(timezone.utc),
            outbound_urls=internal_links,  # used by crawl frontier
        )

    def _extract_canonical(self, soup: BeautifulSoup, current_url: str) -> str | None:
        tag = soup.find("link", rel="canonical")
        if tag and tag.get("href"):
            return urljoin(current_url, tag["href"])
        return None

    def _extract_is_indexable(self, soup: BeautifulSoup) -> bool:
        tag = soup.find("meta", attrs={"name": "robots"})
        if tag:
            content = (tag.get("content") or "").lower()
            if "noindex" in content:
                return False
        return True
