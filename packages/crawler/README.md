# Crawler Package

Safe, robots.txt-aware website crawler for SEO Agent OS. Crawls 25–100 pages per run with sitemap discovery, BFS link traversal, and full HTML extraction.

## Overview

Responsibilities:
- Parse and enforce `robots.txt` rules per-URL
- Discover seed URLs from `sitemap.xml` (and `Sitemap:` directives in robots.txt)
- Fetch HTML pages asynchronously with per-domain rate limiting
- Extract: titles, meta descriptions, H1/H2, canonical, schema.org JSON-LD, images (alt text), word count, internal/external links
- BFS crawl frontier bounded by `max_pages` (25–100) and `crawl_depth` (0–10)
- Produce a `CrawlResult` and `CrawlSummary` for storage

## Architecture

```
CrawlRunner          — orchestrates the full crawl session
├── RobotParser      — fetches + caches robots.txt, answers can_fetch()
├── SitemapParser    — discovers seed URLs from sitemap.xml
└── PageFetcher      — async HTTP with semaphore-based concurrency control
    └── BeautifulSoup + lxml — HTML parsing
```

## Key Classes

| Class | Responsibility |
|---|---|
| `CrawlConfig` | Pydantic config: URL, max_pages, depth, delay_ms, user_agent, respect_robots |
| `CrawlRunner` | BFS crawl orchestrator. `run()` → `CrawlResult` |
| `PageFetcher` | Async HTTP fetcher with rate limiting and HTML parsing. Must be used as async ctx manager |
| `RobotParser` | Fetches robots.txt lazily, answers `can_fetch(url)` |
| `SitemapParser` | Discovers URLs from sitemap index, sub-sitemaps, robots.txt Sitemap: directives |
| `PageRecord` | Normalized single-page data (mirrors DB Page model) |
| `CrawlResult` | Full crawl output: pages list, timing, discovered/crawled counts |
| `CrawlSummary` | Aggregate stats: blocked count, non-indexable, schema count, avg word count |

## Usage

### As a Python library

```python
import asyncio
from packages.crawler import CrawlConfig, CrawlRunner

async def crawl():
    config = CrawlConfig(
        start_url="https://example.com",
        max_pages=50,
        crawl_depth=3,
        delay_ms=500,
        respect_robots=True,
    )
    runner = CrawlRunner(config)
    result = await runner.run()
    summary = runner.summary()

    print(f"Crawled {result.pages_crawled} pages in {result.duration_seconds:.1f}s")
    for page in result.pages:
        print(f"  {page.status_code} {page.url}")

asyncio.run(crawl())
```

### As a Celery task

```python
from packages.crawler.crawl_worker import crawl_website_task

# Enqueue the crawl
task = crawl_website_task.delay(
    crawl_run_id="<uuid>",
    start_url="https://example.com",
    max_pages=50,
    crawl_depth=3,
)
print(f"Task ID: {task.id}")
```

### As a standalone script

```bash
# Basic crawl
python -m packages.crawler.crawl_worker https://example.com

# With options
python -m packages.crawler.crawl_worker https://example.com \
    --max-pages 100 \
    --depth 4 \
    --delay-ms 200 \
    --crawl-run-id 550e8400-e29b-41d4-a716-446655440000
```

## Dependencies

| Package | Purpose |
|---|---|
| `httpx` | Async HTTP client |
| `beautifulsoup4` | HTML parsing |
| `lxml` | Fast XML/HTML parser (sitemap parsing, HTML tree) |
| `tenacity` | Retry with exponential backoff |
| `pydantic` | Config and data models |

Install all at once:
```bash
pip install httpx beautifulsoup4 lxml tenacity pydantic
```

## Configuration (CrawlConfig defaults)

| Field | Default | Description |
|---|---|---|
| `max_pages` | 50 | Max pages to crawl (1–500) |
| `crawl_depth` | 3 | Max link-following depth (0–10) |
| `delay_ms` | 500 | Milliseconds between requests |
| `timeout_ms` | 15,000 | Request timeout in ms |
| `respect_robots` | True | Check robots.txt before fetching |
| `obey_crawl_delay` | True | Honor Crawl-delay in robots.txt |
| `follow_sitemaps` | True | Seed URLs from sitemap.xml first |
| `max_concurrent` | 5 | Concurrent connections (set on CrawlRunner) |
| `user_agent` | SEO-Agent-OS/1.0 | User-Agent header sent with requests |

## DB Integration

`crawl_worker.py` handles DB integration when run as a Celery task or with `--crawl-run-id`:
1. Creates `Page` records (upserted by `url + crawl_run_id`)
2. Updates `CrawlRun` record: `pages_discovered`, `pages_crawled`, `started_at`, `completed_at`, `status`

If the DB is not available, the crawler runs in standalone mode and prints results to stdout.
