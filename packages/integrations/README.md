# Integrations Package

External service connectors: GSC, GA4, PageSpeed, WordPress, GitHub.

## Overview

Provides read/write connectors to external platforms used in the SEO workflow: Google Search Console (performance data), Google Analytics 4 (traffic insights), PageSpeed Insights (core web vitals), WordPress (content publishing), and GitHub (code and schema commits).

## Integrations

### Google Search Console (GSC)
- Fetch site-level and page-level performance data (impressions, clicks, CTR, position)
- Identify top queries and landing pages
- Trigger indexing requests (URL inspection)

### Google Analytics 4 (GA4)
- Fetch traffic summaries and user engagement metrics
- Identify top content by sessions and bounce rate
- Get conversion data for goal tracking

### PageSpeed Insights
- Fetch Core Web Vitals (LCP, FID, CLS) for any URL
- Get performance scores and optimization recommendations

### WordPress
- Create draft posts with content, metadata, and schema
- Update existing posts
- Publish approved content (with approval gate)

### GitHub
- Commit schema JSON-LD files to a configured repository
- Create pull requests for content changes
- Manage repository content via GitHub API

## Responsibilities

- Maintain OAuth2 / API key authentication for each service
- Handle rate limiting and exponential backoff
- Normalize external data into internal schemas
- Manage credential storage (secure, per-business)
- Provide async-friendly client interfaces

## Key Classes / Functions

- `GscClient` — Google Search Console API wrapper
- `Ga4Client` — Google Analytics 4 Data API wrapper
- `PageSpeedClient` — PageSpeed Insights API wrapper
- `WordPressClient` — WordPress REST API / WP CLI wrapper
- `GitHubClient` — GitHub API wrapper for file commits

## Dependencies

- google-api-python-client (GSC, GA4)
- requests (PageSpeed, WordPress, GitHub)
- pydantic
- packages.shared
