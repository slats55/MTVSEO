# API Specification — Autonomous SEO Agent OS

**Status:** Phase 2 — Basic endpoints, audit endpoints TODO

---

## Base URL

```
http://localhost:8000/api/v1
```

---

## Authentication

None implemented yet. TODO: add OAuth2 or API key.

---

## Endpoints

### Health Check

```http
GET /health
```

**Response:** `{"status": "ok"}`

---

## Businesses

### List Businesses

```http
GET /businesses
```

**Response:** `BusinessList`

### Create Business

```http
POST /businesses
{
  "name": "MTV Tech Solutions",
  "website_url": "https://example.com",
  "description": "...",
  "business_type": "Technology",
  "location": "Austin, TX",
  "phone": "+1-512-555-0100",
  "email": "contact@example.com",
  "is_cannabis": false,
  "is_ymyl": false
}
```

**Response:** `BusinessRead` with 201.

### Get Business

```http
GET /businesses/{business_id}
```

**Response:** `BusinessRead` or 404.

### Update Business

```http
PATCH /businesses/{business_id}
{
  "name": "New Name",
  "description": "Updated description"
}
```

**Response:** `BusinessRead` or 404.

---

## Websites

### List Websites

```http
GET /websites?business_id={business_id}
```

**Response:** `WebsiteList`

### Create Website

```http
POST /websites
{
  "business_id": "uuid",
  "domain": "example.com",
  "url": "https://example.com",
  "website_type": "primary|secondary",
  "is_primary": true
}
```

**Response:** `WebsiteRead` with 201.

---

## Crawls

### List Crawl Runs

```http
GET /crawls?website_id={website_id}
```

**Response:** `CrawlRunList`

### Trigger Crawl

```http
POST /crawls
{
  "website_id": "550e8400-e29b-41d4-a716-446655440000",
  "crawl_depth": 3,
  "max_pages": 100
}
```

**Response:** `CrawlRunRead` with 201.

### Get Crawl Status

```http
GET /crawls/{crawl_run_id}/status
```

**Response:** `{ "id": "uuid", "status": "pending", "pages_discovered": 0, "pages_crawled": 0, "error_message": null }`

### Cancel Crawl

```http
POST /crawls/{crawl_run_id}/cancel
```

**Response:** `CrawlRunRead` or 404/409.

---

## Pages

### List Pages

```http
GET /pages?website_id={website_id}& is_indexable=true& has_schema=false
```

**Response:** `PageList`

### Get Page

```http
GET /pages/{page_id}
```

**Response:** `PageRead` or 404.

---

## Planned Endpoints (Not Implemented)

### Audit Reports

```
POST /audits/technical   — Run technical SEO audit
POST /audits/geo         — Run GEO/AI audit
GET  /audits/{audit_id}
```

### Content & Schema

```
POST /content/briefs     — Generate brief
POST /schema/generate     — Generate schema JSON-LD
```

### Publishing

```
POST /publishing/drafts   — Create draft
POST /publishing/drafts/{id}/approve
POST /publishing/jobs     — Publish
```

---

## Environment Configuration

See `.env.example` for required environment variables:

- `DATABASE_URL`: Async database connection (PostgreSQL preferred for prod, SQLite for dev)
- `SYNC_DATABASE_URL`: Sync connection for migrations
- `REDIS_URL`: Redis for Celery/RQ (TODO)
- `HERMES_ENDPOINT`, `HERMES_API_KEY`: AI orchestrator (TODO)
- External API keys: Google Search Console, PageSpeed, etc.

---

## Migrations

```bash
cd services/api
alembic upgrade head
```

Initial migration creates all 20 entity tables based on `services/api/models/`.

---

## Testing

```bash
PYTHONPATH=. pytest tests/ -q
```

Backend smoke tests live in `tests/test_backend_smoke.py`.

---

## Known Limitations (Phase 2)

- No authentication
- No rate limiting
- Crawl worker not implemented (crawls created but never execute)
- No audit endpoints yet
- No content/brief endpoints yet
- Publishing workflow not started

---

*Last updated:* 2025-05-07
*Branch:* `feature/backend-phase2`