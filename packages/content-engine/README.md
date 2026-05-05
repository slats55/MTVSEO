# Content Engine Package

Content generation, optimization, and brief creation.

## Overview

Generates SEO-optimized content briefs and drafts from business profiles and audit data. Optimizes existing content for target keywords and search intent. Enforces brand voice, usefulness checks, and compliance guardrails on all outputs.

## Content Opportunity Score Weights

| Category | Weight |
|---|---|
| Business Value | 25 |
| Search Intent Strength | 20 |
| Ranking Gap | 15 |
| Conversion Likelihood | 20 |
| Content Feasibility | 10 |
| Internal Link Support | 10 |

## Responsibilities

- Keyword research and topic cluster mapping
- Content opportunity scoring and prioritization
- Content brief generation from business profile + audit data
- First-draft content generation with metadata and schema markup
- Content optimization for target keywords and search intent
- Brand voice preservation
- Usefulness and compliance checking
- Internal link embedding suggestions
- Plagiarism / originality verification

## Key Classes / Functions

- `ContentEngine` — main orchestrator
- `KeywordResearcher` — keyword and topic cluster analysis
- `BriefGenerator` — creates structured content briefs
- `ContentDrafter` — generates initial content drafts
- `ContentOptimizer` — improves existing content
- `BrandVoicePreserver` — maintains consistent brand tone
- `ComplianceChecker` — enforces guardrails before output

## Dependencies

- pydantic
- packages.shared
- packages.schema-engine (for inline schema markup)
- Hermes AI (via API calls for generation)
