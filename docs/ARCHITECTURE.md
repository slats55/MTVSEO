# Architecture — Autonomous SEO Agent OS

## 1. System Overview

SEO Agent OS is a modular, polyglot system with a Next.js dashboard, Python FastAPI backend, and a package-based domain layer. The system runs autonomous SEO/GEO audits and generates content — with a mandatory human-in-the-loop before any publishing.

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Next.js Dashboard                            │
│              (Business management, reports, approvals)               │
└──────────────────────────────────┬──────────────────────────────────┘
                                   │ HTTP/REST
┌──────────────────────────────────▼──────────────────────────────────┐
│                         FastAPI Backend                              │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ │
│  │ Crawler  │ │ SEO Audit│ │ GEO Audit│ │ Content  │ │ Reporting│ │
│  │ Package  │ │ Package  │ │ Package  │ │ Engine   │ │ Package  │ │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘ │
│       │            │            │            │            │        │
│  ┌────▼────────────▼────────────▼────────────▼────────────▼────┐  │
│  │                    packages/shared                            │  │
│  │          (models, schemas, constants, utilities)              │  │
│  └─────────────────────────┬────────────────────────────────────┘  │
│                            │ SQLAlchemy 2.0 (async)                │
│  ┌─────────────────────────▼────────────────────────────────────┐  │
│  │                    PostgreSQL 14+                             │  │
│  └───────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────┬──────────────────────────────────┘
                                   │
                    ┌──────────────▼──────────────┐
                    │    Celery + Redis Queue      │
                    │  (async crawl jobs, audits)  │
                    └──────────────────────────────┘
```

---

## 2. Frontend — Next.js / React

**Location:** `apps/web/`

| Concern | Choice |
|---|---|
| Framework | Next.js 14+ (App Router) |
| Language | TypeScript |
| Styling | Tailwind CSS — dark professional theme |
| Server State | TanStack Query (React Query) |
| Client State | Zustand |
| Forms | React Hook Form + Zod |
| Charts | Recharts or Tremor |
| Testing | Jest (unit), Playwright (e2e) |

### Why Next.js?

- SSR/SSG for fast initial page loads on the dashboard
- API routes available for proxying external API calls (protecting API keys)
- Strong TypeScript support across frontend and backend
- Large ecosystem and familiar patterns for React developers

### Folder Structure

```
apps/web/
  src/
    app/               # App Router pages (route groups)
    components/         # Shared UI components (Button, Card, Modal, etc.)
    features/           # Feature-scoped modules (businesses/, crawl/, audit/)
    lib/                # API client, auth helpers, utilities
    types/              # Shared TypeScript types (mirroring shared package)
  public/
  tests/
```

---

## 3. Backend — Python FastAPI

**Location:** `services/api/`

| Concern | Choice |
|---|---|
| Framework | FastAPI (Python 3.11+) |
| ORM | SQLAlchemy 2.0 (async, asyncpg driver) |
| Migrations | Alembic |
| Validation | Pydantic v2 |
| Task Queue | Celery + Redis (RQ as fallback) |
| HTTP Client | httpx (async) |
| Testing | pytest, pytest-asyncio |

### Why FastAPI over Node/Express?

- Python is the dominant language for SEO/GEO tooling (crawling, parsing, AI orchestration)
- Strong async support for I/O-bound crawling workloads
- Pydantic for request/response validation with minimal boilerplate
- Auto-generated OpenAPI docs (Swagger UI) accelerate frontend integration
- Easier integration with AI model providers (MiniMax, Anthropic, OpenAI)

### API Design

- REST API under `/api/v1/` prefix
- All requests validated via Pydantic schemas
- All responses use typed Pydantic models
- Errors return RFC 7807 Problem Details (`application/problem+json`)
- Async endpoints for long-running operations (crawl, audit)
- Sync endpoints for fast reads (fetching scores, listing reports)

### Folder Structure

```
services/api/
  app/
    api/v1/             # Route handlers (businesses, crawl, audit, reports)
    core/               # Config, security, app dependencies
    db/                 # Session management, Alembic setup
    models/             # SQLAlchemy ORM models
    schemas/            # Pydantic request/response schemas
    services/           # Business logic per domain
    worker/             # Celery task definitions
  tests/
  main.py               # FastAPI app factory
  requirements.txt
```

---

## 4. Database — PostgreSQL

| Concern | Choice |
|---|---|
| Primary | PostgreSQL 14+ |
| MVP Fallback | SQLite |
| Connection Pool | asyncpg (async), SQLAlchemy built-in (sync) |
| Indexing | B-tree (default), GIN (JSON columns), hash (unique) |

### Why PostgreSQL over MySQL?

- JSONB columns for storing structured data (schema markup, audit results) with indexing
- Full-text search support for content analysis
- Stronger JSON support and more expressive CTEs
- Better support for async drivers in Python ecosystem

### Schema Management

- Alembic for migration versioning
- Auto-generated migration scripts from SQLAlchemy model changes
- Migration history stored in `alembic_versions/` table

### Key Tables

See `docs/DATA_MODEL.md` for the complete entity relationship diagram and field definitions.

---

## 5. Task Queue — Celery + Redis

| Concern | Choice |
|---|---|
| Broker | Redis 6+ |
| Queue Backend | Celery (Python-first, production-grade) |
| Fallback | RQ (simpler, good for MVP) |

### Why Celery?

- First-class Python support with async task results
- Scheduled tasks (Celery Beat) for recurring audits
- Task routing to different queues (crawl, audit, content)
- Retry policies with exponential backoff
- Supervision and monitoring via Flower (optional)

### Task Types

| Task | Queue | Typical Duration |
|---|---|---|
| `crawl_website` | `crawl` | 2–10 min |
| `run_seo_audit` | `audit` | 1–5 min |
| `run_geo_audit` | `audit` | 1–5 min |
| `generate_content_brief` | `content` | 30–120 sec |
| `draft_content` | `content` | 60–180 sec |
| `generate_report` | `reporting` | 30–60 sec |
| `fetch_gsc_data` | `integrations` | 30–120 sec |

---

## 6. AI / Model Routing

| Concern | Choice |
|---|---|
| Primary AI | MiniMax (via Hermes) |
| Strategy / Content | MiniMax (strong model) |
| Extraction / Parsing | MiniMax (cheap/fast model) |
| Fallback | Anthropic Claude, OpenAI GPT |

### Model Routing Strategy

The orchestrator selects the appropriate model per task:

```
Extraction tasks (crawling, parsing, batch scoring)  →  MiniMax cheap
Strategy tasks (recommendations, opportunity scoring) →  MiniMax strong
Content generation (briefs, drafts, optimization)     →  MiniMax strong + editor review
Compliance review (usefulness check, YMYL flag)     →  MiniMax strong
```

### Integration

- AI calls go through the `packages/shared` AI client wrapper
- All prompts are versioned and stored (for auditability)
- Responses are cached where appropriate (Redis TTL 1 hour)
- Cost tracking per business per month

---

## 7. Package Architecture

Each domain package is independently deployable and testable.

```
packages/
  shared/           # Must have ZERO dependencies on other packages
  crawler/          # Depends on: shared
  seo-audit/       # Depends on: shared, crawler
  geo-audit/        # Depends on: shared, crawler
  content-engine/   # Depends on: shared, seo-audit, geo-audit
  schema-engine/    # Depends on: shared
  reporting/        # Depends on: shared, seo-audit, geo-audit
  integrations/     # Depends on: shared
```

### Dependency Rules

1. No package may depend on `services/api` or `apps/web`
2. `packages/shared` is the only package with zero internal dependencies
3. All packages expose a typed interface via `__init__.py`
4. All packages include unit tests

---

## 8. Storage Strategy

```
storage/
  reports/              # Generated Markdown/PDF reports
  exports/              # CSV, JSON, ZIP export packages
  crawl-snapshots/      # HTML snapshots of crawled pages
  schema-outputs/       # Generated JSON-LD schema files
```

### Storage Backend

- **Local filesystem** (default for MVP): `./storage/` directory
- **S3-compatible** (production): configurable via `STORAGE_BACKEND=s3` env var
- All stored content is immutable (new file per run, never overwrite)
- File paths include run ID and timestamp for deduplication

---

## 9. Security Architecture

| Concern | Approach |
|---|---|
| API Authentication | Bearer token (JWT) with short expiry |
| Database Credentials | Environment variables only, never in code |
| External API Keys | Encrypted at rest, injected via environment |
| File Access | Signed URLs for user downloads |
| Rate Limiting | Per-IP and per-token limits via middleware |
| Input Validation | Pydantic schemas validate all input |
| SQL Injection | SQLAlchemy ORM (parameterized queries) |
| XSS | Content-Security-Policy headers, sanitized output |
| CSRF | SameSite cookies, CORS configuration |

---

## 10. Compliance Architecture

Compliance is enforced at three layers:

### Layer 1 — Data Model
- `ContentDraft.compliance_flags` JSONB field records all checks passed/failed
- `Business.is_cannabis` flag triggers cannabis-specific checks
- `Business.is_ymyl` flag triggers YMYL human-review requirement

### Layer 2 — Agent Prompts
- All generation prompts include compliance instructions
- Prompts reject fake claims, reviews, statistics
- Prompts enforce brand voice and usefulness criteria

### Layer 3 — Publishing Gate
- `PublishingJob.status` is PENDING_REVIEW before any content goes live
- Only users with `publish` permission can approve
- WordPress/GitHub pushes are blocked unless `approval_status=APPROVED`

---

## 11. Deployment Overview

| Environment | Description |
|---|---|
| Development | Local Python venv + Next.js dev server |
| Staging | Docker Compose (API + Redis + PostgreSQL) |
| Production | Kubernetes or cloud VMs with managed DB |

### Environment Variables

See `.env.example` for the full list. Critical variables:

```
DATABASE_URL             # PostgreSQL connection string
SYNC_DATABASE_URL        # For Alembic migrations
REDIS_URL                # Celery broker
HERMES_API_KEY           # AI provider
HERMES_ENDPOINT          # Hermes agent endpoint
GOOGLE_API_KEY           # Google APIs
SECRET_KEY               # JWT signing key
APP_ENV                  # development | staging | production
STORAGE_BACKEND          # local | s3
STORAGE_PATH             # Local path or S3 bucket name
```

---

## 12. Key Architectural Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Next.js over Vue/Angular | Familiar, SSR, API routes | Orion's preference + ecosystem |
| FastAPI over Express/Nest | Python SEO tooling ecosystem | Crawling + AI orchestration fit |
| PostgreSQL over MySQL | JSONB + async driver quality | Structured data + SEO workloads |
| Celery over BullMQ | Python-first | Natural fit with FastAPI backend |
| MiniMax as primary AI | Cost + capability | Hermes model router |
| packages/shared | Zero internal dependencies | Prevents circular imports, clear boundaries |
| Markdown-first reports | Fast iteration | HTML/PDF can be layered on later |

See `docs/DECISIONS.md` for the full decision log.

---

*Document version: 1.0 — Phase 0*
*Project: Autonomous SEO Agent OS*
*Owner: Orion (MT Val)*
