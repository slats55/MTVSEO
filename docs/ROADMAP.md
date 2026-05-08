# Roadmap — Autonomous SEO Agent OS

**Status:** Phase 2 — Backend Stabilization

---

## Phases Overview

| Phase | Focus |
|-------|-------|
| 0 | Research & Setup |
| 1 | Data Layer & Ingestion |
| 2 | SEO Audit Engine |
| 3 | GEO / AI Visibility Engine |
| 4 | Content Engine |
| 5 | Schema Engine |
| 6 | Internal Linking |
| 7 | Report Generator |
| 8 | Dashboard MVP |
| 9 | Integrations |
| 10 | Monitoring & Refinement |

Current: Phase 2 completion and Phase 2A stabilization.

---

## Phase 2 (Target Completion)

- [x] Backend smoke tests
- [x] Alembic migration verification
- [x] SQLite fallback works locally
- [x] Frontend build fix
- [ ] Celery/RQ worker implementation
- [ ] Audit endpoints (POST /audits/technical, /audits/geo)
- [ ] Frontend React Query wiring
- [ ] Documentation foundation (this doc, API_SPEC, AGENT_ROLES, etc.)

---

## Phase 3+ (Future)

- Integrations (GSC, GA4, PageSpeed)
- Publishing workflow (draft → approve → publish with rollback)
- Internal link recommender
- Advanced content optimization
- Multi-user auth
- Monitoring/alerting

---

## Milestones

- M1: Backend stable locally (import clean, tests green)
- M2: Frontend–Backend integration (React Query → API)
- M3: Integrations package (choose one: GSC first)
- M4: Human Approval & Publishing Workflow
- M5: First production audit run (manual)

---

*Last updated:* 2025-05-07
*Branch:* `feature/backend-phase2`