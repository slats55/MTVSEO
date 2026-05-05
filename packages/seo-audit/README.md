# SEO Audit Package

Technical SEO analysis engine and scoring.

## Overview

Analyzes crawled pages against technical SEO best practices: titles, meta descriptions, heading structure, canonical tags, HTTP status codes, internal links, image optimization, structured data, and more. Produces a 0–100 SEO score with weighted category breakdowns and prioritized recommendations.

## SEO Score Weights

| Category | Weight |
|---|---|
| Crawlability | 20 |
| Indexability | 20 |
| Metadata / On-page | 15 |
| Site Architecture / Internal Links | 15 |
| Performance / Mobile / Accessibility | 15 |
| Structured Data | 10 |
| Security / Basic Trust | 5 |

## Responsibilities

- Analyze page-level SEO elements (titles, meta, headings, canonicals)
- Check HTTP response codes and redirect chains
- Detect duplicate/missing meta tags
- Validate heading hierarchy (H1 → H2 → H3)
- Identify broken internal/external links
- Check image alt text and lazy loading
- Validate structured data (JSON-LD presence and syntax)
- Compute per-page and site-wide SEO scores
- Generate prioritized issue list with severity
- Produce actionable recommendations per issue

## Key Classes / Functions

- `SeoAuditEngine` — main audit orchestrator
- `PageAnalyzer` — per-page analysis
- `ScoreCalculator` — weighted score computation
- `IssueDetector` — rule-based issue identification
- `RecommendationGenerator` — produces prioritized action items

## Dependencies

- beautifulsoup4
- lxml
- pydantic
- packages.shared
