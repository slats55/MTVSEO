# Crawler Package

Website crawling with robots.txt and sitemap awareness.

## Overview

Safely crawls target websites: respects `robots.txt`, follows sitemaps, extracts HTML content, parses metadata, and builds a link graph. Limits crawl depth to 25–100 pages per run.

## Responsibilities

- robots.txt parsing and enforcement
- sitemap.xml discovery and parsing
- HTML fetching with rate limiting (configurable delay between requests)
- HTML parsing: titles, meta descriptions, headings, canonicals, images, links
- PageSnapshot creation: raw HTML + structured extraction
- Link graph construction (internal vs. external links)
- Crawl job state management (start, pause, resume, cancel)
- Error handling: timeouts, DNS failures, SSL errors, non-HTML responses

## Key Classes / Functions

- `Crawler` — main crawl orchestrator
- `RobotParser` — wraps robots.txt rules
- `SitemapParser` — discovers URLs from XML sitemaps
- `HtmlFetcher` — async HTTP client with retry/backoff
- `HtmlParser` — BeautifulSoup-based HTML extractor
- `LinkGraphBuilder` — constructs directed graph of internal pages

## Usage

```python
from packages.crawler import Crawler, CrawlerConfig

config = CrawlerConfig(
    start_url="https://example.com",
    max_pages=50,
    respect_robots=True,
    delay_ms=500,
)
crawler = Crawler(config)
result = await crawler.run()
```

## Dependencies

- httpx (async HTTP)
- beautifulsoup4
- lxml (HTML/XML parsing)
- tenacity (retry logic)
