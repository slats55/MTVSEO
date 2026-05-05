# packages/crawler/robots_parser.py
"""robots.txt parsing and per-URL crawl permission enforcement."""

import asyncio
from urllib.parse import urljoin, urlparse

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from packages.shared.logging import get_logger

logger = get_logger(__name__)


class RobotParser:
    """Fetches and parses robots.txt for a given domain, then answers can_fetch() queries.
    
    Thread-safe for use across concurrent async tasks.
    """

    def __init__(
        self,
        domain: str,
        user_agent: str = "*",
        timeout_ms: int = 10_000,
    ) -> None:
        self.domain = domain
        self.user_agent = user_agent
        self.timeout_ms = timeout_ms
        self._rp: httpx._models.Response | None = None  # robotparser result
        self._fetched = False
        self._lock = asyncio.Lock()

    @property
    def robots_url(self) -> str:
        base = f"https://{self.domain}" if not self.domain.startswith(("http://", "https://")) else self.domain
        return f"{base.rstrip('/')}/robots.txt"

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        reraise=True,
    )
    async def _fetch(self) -> None:
        async with httpx.AsyncClient(timeout=self.timeout_ms / 1000) as client:
            response = await client.get(self.robots_url)
            response.raise_for_status()
            self._rp = response

    async def ensure_fetched(self) -> None:
        """Fetch robots.txt if not already fetched. Safe to call multiple times."""
        if self._fetched:
            return
        async with self._lock:
            if self._fetched:
                return
            try:
                await self._fetch()
                logger.info("Fetched robots.txt for %s", self.domain)
            except httpx.HTTPError as exc:
                logger.warning("Could not fetch robots.txt for %s: %s — allowing all paths", self.domain, exc)
            finally:
                self._fetched = True

    def can_fetch(self, url: str) -> bool:
        """Return True if the given URL is allowed to be crawled, False otherwise.
        
        If robots.txt has not been fetched yet, returns True (fail open).
        """
        if self._rp is None:
            # Not fetched yet — fail open, rely on runtime enforcement
            return True

        rp = _RobotFileParser()
        rp.parse(self._rp.text.splitlines())
        return rp.can_fetch(self.user_agent, url)

    def get_crawl_delay(self) -> float | None:
        """Return the Crawl-delay the robotparser specifies for our user agent, or None."""
        if self._rp is None:
            return None
        rp = _RobotFileParser()
        rp.parse(self._rp.text.splitlines())
        try:
            delay = rp.crawl_delay(self.user_agent)
            return None if delay is None else float(delay)
        except (ValueError, TypeError):
            return None


# ─── stdlib robotparser shim (imported lazily to avoid top-level dependency issues) ───


def _RobotFileParser():
    """Lazily import RobotFileParser to avoid import errors in some environments."""
    from urllib.robotparser import RobotFileParser
    return RobotFileParser()
