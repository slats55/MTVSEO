# Shared Package

Shared types, models, utilities, and constants across all packages.

## Overview

Contains all cross-cutting concerns: SQLAlchemy database models, Pydantic schemas, enums, constants, utility functions, and compliance rules. Imported by all other packages — must have zero internal dependencies on other packages.

## Contents

### Database Models (SQLAlchemy)

All entity models: User, Business, Website, Competitor, CrawlRun, Page, PageSnapshot, SeoIssue, GeoIssue, Keyword, TopicCluster, ContentBrief, ContentDraft, InternalLinkOpportunity, SchemaDraft, PublishingJob, Report, MetricSnapshot, AgentTask, AgentRunLog.

### Pydantic Schemas

Request/response schemas for API validation: BusinessCreate, WebsiteCreate, CrawlStart, AuditRun, etc.

### Constants

- Score weights (SEO, GEO, Content Opportunity)
- Issue severity levels
- HTTP status code categories
- Content compliance flags
- Business type enums
- Schema type registry

### Utilities

- URL helpers (normalization, extraction, path joining)
- Text utilities (truncation, slugification, reading time)
- Date/time helpers (ISO formatting, age computation)
- Score computation helpers
- File path builders for storage directories

### Compliance Rules

- YMYL topic classification
- Cannabis business flagging
- Content usefulness checklist
- Black-hat tactic detection patterns

## Structure

```
packages/shared/
  models/          # SQLAlchemy ORM models
  schemas/         # Pydantic schemas
  constants/       # Enums, weights, flags
  utils/           # Pure utility functions
  compliance/      # Compliance rule definitions
  __init__.py
```

## Dependencies

- sqlalchemy (core only — no alembic here)
- pydantic
- python-dateutil
