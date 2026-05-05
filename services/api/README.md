# API Service

FastAPI backend for the SEO Agent OS.

## Overview

Handles all business logic: crawl orchestration, SEO/GEO analysis, content generation, schema creation, report assembly, and external integrations. Exposes a REST API consumed by the web dashboard.

## Tech Stack

- **Framework:** FastAPI (Python 3.11+)
- **ORM:** SQLAlchemy 2.0 (async)
- **Migrations:** Alembic
- **Validation:** Pydantic v2
- **Task Queue:** Celery + Redis (or RQ for simpler deployments)
- **Database:** PostgreSQL (primary), SQLite (MVP only)

## Structure

```
services/api/
  app/
    api/            # API route handlers
    core/           # Config, security, dependencies
    db/             # Session management, migrations
    models/         # SQLAlchemy models
    schemas/        # Pydantic request/response schemas
    services/       # Business logic (orchestrated per domain)
    worker/         # Celery tasks
  tests/
  main.py           # FastAPI app entry point
  requirements.txt
```

## Getting Started

```bash
cd services/api
pip install -r requirements.txt
alembic upgrade head
uvicorn main:app --reload --port 8000
```

## API Prefix

All routes are prefixed with `/api/v1/`.
