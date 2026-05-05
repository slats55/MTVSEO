# GEO Audit Package

GEO (Generative Engine Optimization) and AI visibility analysis.

## Overview

Audits how well a website is accessible to and citable by AI systems (ChatGPT, Gemini, Perplexity, Claude, etc.). Checks AI crawler access, entity clarity, content depth, citability signals, structured data for entities, llms.txt generation, and brand authority signals. Produces a 0–100 GEO score.

## GEO Score Weights

| Category | Weight |
|---|---|
| AI Crawler Accessibility | 15 |
| Entity Clarity | 15 |
| Citability | 25 |
| Content Depth / Helpfulness | 20 |
| Schema / Structured Data | 10 |
| Brand Authority Signals | 10 |
| llms.txt / AI Readability | 5 |

## Responsibilities

- Detect AI crawler directives in robots.txt
- Assess entity clarity: business name, location, contact, schema markup
- Score content for citability: factual density, named entities, source citations
- Evaluate content depth and E-E-A-T signals
- Check structured data completeness (Organization, LocalBusiness, etc.)
- Generate llms.txt drafts
- Assess backlink and brand mention signals
- Produce GEO recommendations

## Key Classes / Functions

- `GeoAuditEngine` — main GEO audit orchestrator
- `AiCrawlerChecker` — detects AI crawler access issues
- `EntityClarityScorer` — evaluates entity signal strength
- `CitabilityScorer` — assesses how easily AI can cite content
- `LlmsTxtGenerator` — creates llms.txt from crawl data

## Dependencies

- httpx
- beautifulsoup4
- pydantic
- packages.shared
