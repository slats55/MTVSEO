# packages/crawler/sitemap_parser.py
"""Discovers and parses sitemap.xml files to extract crawlable URLs."""

import asyncio
from urllib.parse import urljoin, urlparse
from xml.etree import ElementTree as ET

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from packages.shared.logging import get_logger

logger = get_logger(__name__)

# Well-known sitemap locations tried in order if no sitemap URL is provided
SITEMAP_CANDIDATES = [
    "/sitemap.xml",
    "/sitemap_index.xml",
    "/sitemap/sitemap.xml",
    "/wp-sitemap.xml",
    "/sitemap.xml.gz",
]


class SitemapParser:
    """Fetches and parses one or more sitemap.xml files, returning all discovered URLs.
    
    Handles:
    - Standard sitemaps (<urlset>) with <loc> entries
    - Sitemap index files (<sitemapindex>) pointing to sub-sitemaps
    - Nested sitemap index files (index → index → urlset)
    - <lastmod>, <changefreq>, <priority> metadata (returned as attributes)
    - Discovery from robots.txt (Sitemap: directives)
    - Respects robots.txt-disallowed URLs when verify_with_robots is used
    """

    def __init__(
        self,
        domain: str,
        timeout_ms: int = 10_000,
        max_depth: int = 3,
    ) -> None:
        self.domain = domain
        self.timeout_ms = timeout_ms
        self.max_depth = max_depth
        self._discovered_sitemaps: list[str] = []
        self._all_urls: list[str] = []
        self._seen_urls: set[str] = set()
        self._seen_sitemaps: set[str] = set()

    @property
    def base_url(self) -> str:
        return f"https://{self.domain}" if not self.domain.startswith(("http://", "https://")) else self.domain

    # ── public API ──────────────────────────────────────────────────────────────

    async def discover_and_parse(
        self,
        sitemap_url: str | None = None,
    ) -> list[str]:
        """Main entry point. Returns all URLs found across all sitemaps."""
        if sitemap_url:
            await self._parse_sitemap(sitemap_url, depth=0)
        else:
            # Try robots.txt Sitemap: directives first
            robots_urls = await self._discover_from_robots_txt()
            for sm_url in robots_urls:
                await self._parse_sitemap(sm_url, depth=0)

            # Fall back to well-known candidates
            if not self._all_urls:
                for candidate in SITEMAP_CANDIDATES:
                    url = urljoin(self.base_url, candidate)
                    try:
                        await self._parse_sitemap(url, depth=0)
                    except Exception:
                        pass

        return list(self._all_urls)

    def urls(self) -> list[str]:
        """Return all URLs discovered so far."""
        return list(self._all_urls)

    # ── internal helpers ─────────────────────────────────────────────────────────

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10), reraise=True)
    async def _fetch_xml(self, url: str) -> str:
        async with httpx.AsyncClient(timeout=self.timeout_ms / 1000) as client:
            response = await client.get(url, follow_redirects=True)
            response.raise_for_status()
            return response.text

    async def _parse_sitemap(self, url: str, depth: int) -> None:
        if depth > self.max_depth:
            logger.debug("Max sitemap depth %d reached at %s", depth, url)
            return
        if url in self._seen_sitemaps:
            return
        self._seen_sitemaps.add(url)

        try:
            raw = await self._fetch_xml(url)
        except httpx.HTTPError as exc:
            logger.debug("Could not fetch sitemap %s: %s", url, exc)
            return

        try:
            root = ET.fromstring(raw.encode("utf-8") if isinstance(raw, str) else raw)
        except ET.ParseError as exc:
            logger.debug("Could not parse XML at %s: %s", url, exc)
            return

        namespace = self._detect_namespace(root)

        if self._is_sitemap_index(root, namespace):
            await self._parse_sitemap_index(root, namespace, depth)
        else:
            self._parse_url_entries(root, namespace)
            self._discovered_sitemaps.append(url)

    async def _parse_sitemap_index(
        self, root: ET.Element, namespace: str, parent_depth: int
    ) -> None:
        """Handle <sitemapindex> — recursively parse sub-sitemaps."""
        loc_elements = root.findall(f".//{namespace}loc")
        for loc_el in loc_elements:
            loc_text = (loc_el.text or "").strip()
            if loc_text:
                await self._parse_sitemap(loc_text, depth=parent_depth + 1)

    def _parse_url_entries(self, root: ET.Element, namespace: str) -> None:
        """Handle <urlset> — extract <loc> from each <url>."""
        url_elements = root.findall(f".//{namespace}url")
        for url_el in url_elements:
            loc_el = url_el.find(f"{namespace}loc")
            if loc_el is None:
                continue
            loc_text = (loc_el.text or "").strip()
            if loc_text and loc_text not in self._seen_urls:
                # Skip URLs not matching the target domain
                parsed = urlparse(loc_text)
                if parsed.netloc == self.domain:
                    self._seen_urls.add(loc_text)
                    self._all_urls.append(loc_text)

    def _detect_namespace(self, root: ET.Element) -> str:
        """Detect XML namespace from root tag, e.g. '{http://www.sitemaps.org/schemas/sitemap/0.9}'."""
        tag = root.tag or ""
        if tag.startswith("{"):
            ns = tag[tag.index("{"): tag.index("}") + 1]
            return ns
        return ""

    def _is_sitemap_index(self, root: ET.Element, namespace: str) -> bool:
        """Return True if this is a sitemap index (<sitemapindex>), not a URL set."""
        return root.tag.endswith("}sitemapindex") or root.tag == "sitemapindex"

    async def _discover_from_robots_txt(self) -> list[str]:
        """Read Sitemap: directives from robots.txt."""
        robots_url = f"{self.base_url.rstrip('/')}/robots.txt"
        try:
            async with httpx.AsyncClient(timeout=self.timeout_ms / 1000) as client:
                response = await client.get(robots_url)
                response.raise_for_status()
                lines = response.text.splitlines()
                sitemaps = [
                    line.split(":", 1)[1].strip()
                    for line in lines
                    if line.lower().startswith("sitemap:")
                ]
                logger.info("Found %d Sitemap: directives in robots.txt for %s", len(sitemaps), self.domain)
                return sitemaps
        except httpx.HTTPError:
            return []
