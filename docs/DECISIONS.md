# Architectural Decisions — Autonomous SEO Agent OS

**Status:** Phase 2 — Backend Stabilization

---

This doc records key decisions and their rationale. New decisions should be added chronologically as the project evolves.

---

## AD-001: FastAPI over Flask

**Decision:** Use FastAPI for the backend API.

**Rationale:**

- Automatic OpenAPI schema generation
- Async support out of the box for HTTP operations (crawling, DB access)
- Pydantic integration for request/response validation
- Higher performance than Flask for I/O-bound workloads

**Trade-offs:** Smaller ecosystem than Django/Flask, but sufficient for our scope.

---

## AD-002: SQLAlchemy 2.0 + Async

**Decision:** Use SQLAlchemy 2.0 with asyncpg driver for PostgreSQL. SQLite as MVP fallback.

**Rationale:**

- Async DB access matches FastAPI async pattern
- Asyncpg provides high-performance PostgreSQL connectivity
- SQLAlchemy is mature, well-documented
- SQLite allows local dev without Docker

**Trade-offs:** Async SQLAlchemy has some gotchas (must use `await db.execute()` pattern, need `AsyncSession` everywhere).

---

## AD-003: Alembic for Migrations

**Decision:** Use Alembic with autogenerate for schema evolution.

**Rationale:**

- Already part of SQLAlchemy ecosystem
- Supports both SQLite and PostgreSQL
- Manual tweaking needed for complex changes anyway

**Convention:** Run `alembic upgrade head` after every model change. Commit migration files.

---

## AD-004: Package Names Use Underscores

**Decision:** Rename package directories that previously had hyphens to underscores:

- `seo-audit/` → `seo_audit/`
- `geo-audit/` → `geo_audit/`
- `content-engine/` → `content_engine/`
- `schema-engine/` → `schema_engine/`

**Rationale:**

- Python package names cannot contain hyphens; hyphens break imports (`import seo-audit` invalid)
- Underscores are PEP 8-compliant
- Consistent with `packages/shared/`

---

## AD-005: Monorepo with Namespace Packages

**Decision:** Keep all packages under `packages/` directory. Enable `from packages.seo_audit import ...` imports.

**Rationale:**

- Single repo easier to coordinate
- Shared types in `packages/shared/`
- Can use namespace package pattern with `pyproject.toml` to allow root on PYTHONPATH

---

## AD-006: Next.js with TypeScript for Dashboard

**Decision:** Use Next.js 14, React 18, TypeScript, Tailwind CSS.

**Rationale:**

- Client-side routing ideal for dashboard UX
- App Router modern standard
- Tailwind speeds up UI development
- TypeScript catches integration bugs early

**Constraint:** Dashboard evolves independently; build should succeed even if backend not running.

---

## AD-007: Human-in-the-loop Publishing

**Decision:** Never auto-publish. All content posting requires explicit human action.

**Rationale:**

- Prevents accidental spam/poor content
- Gives business owner control
- Compliance requirement for YMYL/cannabis
- Matches product philosophy

**Mechanism:** Publishing endpoints return draft IDs; UI requires a second "Publish" click.

---

## AD-008: Never Generate Fake Claims

**Decision:** Content Brief/Draft/Editor must never:

- Invent reviews/testimonials
- Create fake credentials/awards
- Make up statistics without real data
- Claim partnerships/affiliations not real

**Rationale:**

- Black-hat SEO and unethical
- Violates Google guidelines
- Harmful to brand trust
- Regulatory risk

**Enforcement:** QA agent must review outputs for fake claims. Compliance guardrails flag violations.

---

## AD-009: No Database Redesign for Phase 2

**Decision:** Stick with the 20-entity model from DATA_MODEL.md. Do not add tables during Phase 2 unless required for MVP flow.

**Rationale:**

- Focus is stabilization and integration
- Schema changes require migrations and tests
- Avoid scope creep

**Planned DB additions:**

- `Audit` table (seo_audit + geo_audit run results)
- `ContentPlan` table
- `SchemaPlan` table
- Possibly `PublishingApproval` table

Will add in Phase 3+ carefully with migration scripts.

---

## AD-010: No RabbitMQ — Use Redis or PostgreSQL Broker

**Decision:** Defer Celery/RQ choice. Use PostgreSQL as Celery broker for initial worker implementation if needed.

**Rationale:**

- Redis not required for MVP
- PostgreSQL removes external dependency
- Can switch to Redis later if workload justifies it

**Backup:** If Celery proves too heavy, switch to RQ (simpler).

---

## AD-011: Verification Scripts as Contract

**Decision:** `scripts/verify_local.py` is the "self-test" that any new agent must run before committing.

**Rationale:**

- Provides immediate feedback on environment readiness
- Encodes local dev expectations
- Catches broken imports quickly
- Should return 0 on pass, non-zero on fail

**Usage:** Run after `pip install -r requirements*.txt`.

---

## AD-012: Plain Markdown Reports

**Decision:** Report package outputs Markdown by default. PDF generators are later.

**Rationale:**

- Markdown is human-readable
- Easy to convert to HTML or PDF later
- Quick to iterate

**Future:** Add PDF export via WeasyPrint or headless Chrome if needed.

---

## AD-013: No External Storage in Phase 2

**Decision:** Keep reports, crawl snapshots, exports under `storage/` directory. No S3/cloud storage yet.

**Rationale:**

- Simpler local development
- No IAM credentials to manage
- Can add cloud adapter later

---

## AD-014: Keep REST, Not GraphQL

**Decision:** Use REST endpoints, not GraphQL.

**Rationale:**

- Simpler for Next.js frontend (React Query + REST)
- Easier to secure/rate-limit
- Less moving parts
- Good enough for data shapes needed

**Future:** Consider GraphQL only if dashboard requires complex nested queries that cause N+1.

---

## AD-015: Pydantic for All Schema Validation

**Decision:** All request/response bodies and internal data structures use Pydantic models.

**Rationale:**

- Single validation layer throughout
- Easy conversion to/from JSON
- Type hints and runtime checks
- Matches FastAPI pattern

---

## AD-016: Async Crawler but Optional Celery

**Decision:** Crawler (`packages/crawler`) is an async library. Can run as:

- Direct library call from API route (blocking — small sites)
- Celery task (preferred for production)

**Rationale:**

- Flexibility in deployment
- Async design accelerates I/O-bound crawling
- Can run synchronously for simple local runs

**Note:** Actual Celery task still TODO.

---

## Decisions Pending

- Which LLM provider for content generation? (MiniMax via Hermes likely)
- How to store Page snapshots? (raw HTML? rendered text? both)
- Should we add a local embedding store for semantic search? (Phase 5 maybe)
- Which React state library? (Zustand? Context? React Query is enough for now)

---

*Last updated:* 2025-05-07
*Branch:* `feature/backend-phase2`