# GEO / AI Visibility Audit Package

Analyzes website content for readiness in AI search systems (ChatGPT, Claude, Perplexity, Google Gemini, AI-powered search). Separate from traditional SEO — focuses on how well content can be cited, understood, and used as a source by AI systems.

## Overview

Responsibilities:
- Check AI crawler access via robots.txt (GPTBot, ClaudeBot, PerplexityBot, Google-Extended, CCBot)
- Detect or draft llms.txt (site structure file for AI systems)
- Score page citability (can this page serve as a direct AI source?)
- Check entity optimization (business clearly defined, sameAs schema, social profiles)
- Assess AI answer readiness (does content answer customer questions?)
- Compute 0-100 GEO score with weighted category breakdown

## Score Model (0-100)

| Category | Weight | Description |
|---|---|---|
| AI Crawler Access | 15 | Are friendly AI bots allowed in robots.txt? |
| Entity Clarity | 15 | Is the business clearly defined with schema + sameAs? |
| Citability | 25 | Can AI cite this page as a direct source? |
| Content Depth | 20 | Does content answer questions with sufficient depth? |
| Schema | 10 | Is structured data present and correct? |
| Brand Authority | 10 | Are trust/proof signals present? |
| LLM Readability | 5 | Is llms.txt present and well-structured? |

## Architecture

```
GeoAuditReporter          — orchestrates all analyzers
├── crawler_checker       — robots.txt AI bot directive analysis
├── llms_generator       — llms.txt detection + draft generator
├── citability_scorer    — per-page citability scoring (0-100)
├── entity_checker       — Organization schema, sameAs, social profiles
├── ai_readiness_checker — question-targeting, service depth, FAQ format
└── scorer               — weighted score computation from issues + metrics
```

## Usage

```python
from packages.geo_audit import GeoAuditReporter

reporter = GeoAuditReporter(domain, crawl_result)
report = reporter.run(robots_txt_content=robots_txt_content)

print(f"GEO Score: {report.score.total}/100 ({report.score.grade()})")
for issue in report.issues:
    print(f"  [{issue.severity.value}] {issue.title}")
```

CLI:
```bash
python -m packages.geo_audit crawl_result.json --robots robots.txt --domain example.com
```

## Dependencies

- `packages/crawler` (PageRecord, CrawlResult types)
- `packages/shared` (logging, exceptions)
- Standard library: `urllib.parse`
