# packages/crawler — Safe, robots.txt-aware website crawler.
#
# Public API:
#   CrawlConfig   — configuration for a crawl run
#   CrawlResult   — full crawl output (pages, timing, stats)
#   CrawlSummary  — aggregate summary suitable for DB storage
#   PageRecord    — normalized single-page data
#   CrawlRunner   — main orchestrator (run() → CrawlResult)
#   PageFetcher   — async HTTP fetcher with rate limiting
#   RobotParser   — robots.txt enforcement
#   SitemapParser — sitemap.xml discovery and parsing
#
# Usage:
#   from .crawler import CrawlConfig, CrawlRunner
#   config = CrawlConfig(start_url="https://example.com", max_pages=50)
#   runner = CrawlRunner(config)
#   result = await runner.run()

from .models import (
    CrawlConfig,
    CrawlResult,
    CrawlSummary,
    PageRecord,
)
from .crawl_runner import CrawlRunner
from .page_fetcher import PageFetcher
from .robots_parser import RobotParser
from .sitemap_parser import SitemapParser

__all__ = [
    "CrawlConfig",
    "CrawlResult",
    "CrawlSummary",
    "PageRecord",
    "CrawlRunner",
    "PageFetcher",
    "RobotParser",
    "SitemapParser",
]
