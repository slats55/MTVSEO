# Agent Handoff — Autonomous SEO Agent OS

**Project:** Autonomous SEO Agent OS  
**Status:** PROJECT STARTED — Phase 0 (Research & Setup)  
**Created:** 2026-05-05  
**Owner:** Orion (MT Val)

---

## What Is This Project

Build a production-grade autonomous SEO and GEO agent system for Orion's own businesses:
- MTV Tech Solutions
- Country Roads Car Services  
- Green Culture (cannabis — compliance-first)
- Future local service businesses, ecommerce, SaaS, or content sites

The system must: audit websites, understand the business, research opportunities, create SEO/GEO strategies, generate/optimize content, recommend internal links, create schema, monitor rankings/performance, produce reports, and eventually publish approved changes automatically.

**Inspired by:** geo-seo-claude (architecture), SEO.AI (product category). Build original, not cloned.

---

## Project Location

```
/mnt/c/Users/mtval/Projects/seo-agent-os/
```

---

## Core Principles (Non-Negotiable)

1. No fake claims, reviews, testimonials, credentials, awards, or statistics
2. No doorway pages, spun content, keyword stuffing, hidden text, cloaking, or manipulative links
3. No auto-publish without approval mode
4. No scraping violating terms — use approved APIs
5. No overwriting files without backups, git commits, rollback plans, and clear diffs
6. Every content output must pass usefulness check (real customer question? business-specific? includes real expertise/proof?)
7. YMYL/regulated topics require human review
8. Cannabis SEO includes compliance checks for law, platform rules, age restrictions

---

## Tech Stack

- **Frontend:** Next.js / React — clean dashboard, dark professional theme
- **Backend:** Python FastAPI (preferred for SEO crawling/AI orchestration)
- **Database:** PostgreSQL (preferred), SQLite (MVP only)
- **Queue:** Celery/RQ (Python) or BullMQ (Node)
- **AI:** Hermes agents using MiniMax + other models (model router: cheap for extraction, strong for strategy/content)
- **Storage:** Reports, markdown drafts, JSON audit results, screenshots, SERP snapshots

---

## Project Structure

```
seo-agent-os/
  apps/
    web/          # Next.js/React dashboard
  services/
    api/          # FastAPI backend
  packages/
    crawler/      # Website crawling
    seo-audit/    # Technical SEO analysis
    geo-audit/    # GEO/AI visibility analysis
    content-engine/   # Content generation/optimization
    schema-engine/    # JSON-LD schema generation
    reporting/         # Report generation
    integrations/     # GSC, GA4, PageSpeed, WordPress, GitHub
    shared/           # Shared utilities, types, DB models
  docs/           # Project documentation
  scripts/        # Utility scripts
  tests/          # Test suite
  storage/
    reports/
    exports/
    crawl-snapshots/
```

---

## Required Documents to Produce

| Doc | Status |
|-----|--------|
| README.md | TODO |
| .env.example | TODO |
| docs/PROJECT_BRIEF.md | TODO |
| docs/ARCHITECTURE.md | TODO |
| docs/AGENT_ROLES.md | TODO |
| docs/ROADMAP.md | TODO |
| docs/DATA_MODEL.md | TODO |
| docs/API_SPEC.md | TODO |
| docs/SEO_AUDIT_SCORING.md | TODO |
| docs/GEO_AUDIT_SCORING.md | TODO |
| docs/CONTENT_WORKFLOW.md | TODO |
| docs/PUBLISHING_SAFETY.md | TODO |
| docs/COMPLIANCE_GUARDRAILS.md | TODO |
| docs/AGENT_HANDOFF.md | DONE (this file) |
| docs/DECISIONS.md | TODO |

---

## Core Database Entities

- User, Business, Website, Competitor
- CrawlRun, Page, PageSnapshot
- SeoIssue, GeoIssue
- Keyword, TopicCluster
- ContentBrief, ContentDraft
- InternalLinkOpportunity
- SchemaDraft
- PublishingJob
- Report, MetricSnapshot
- AgentTask, AgentRunLog

---

## Scoring Model

**Technical SEO Score (0-100):**
- Crawlability: 20
- Indexability: 20
- Metadata/on-page: 15
- Site architecture/internal links: 15
- Performance/mobile/accessibility: 15
- Structured data: 10
- Security/basic trust: 5

**GEO Score (0-100):**
- AI crawler accessibility: 15
- Entity clarity: 15
- Citability: 25
- Content depth/helpfulness: 20
- Schema/structured data: 10
- Brand authority signals: 10
- llms.txt/readability for AI systems: 5

**Content Opportunity Score:**
- Business value: 25
- Search intent strength: 20
- Ranking gap: 15
- Conversion likelihood: 20
- Content feasibility: 10
- Internal link support: 10

---

## MVP Commands / UI Actions

- add-business
- crawl-site
- run-technical-audit
- run-geo-audit
- generate-llms-txt
- generate-schema
- build-keyword-map
- create-content-plan
- create-content-brief
- draft-content
- optimize-page
- suggest-internal-links
- generate-report
- export-implementation-package
- publish-draft

---

## MVP Definition of Done

- [ ] Can add a business website
- [ ] System crawls site safely
- [ ] System runs technical SEO audit
- [ ] System runs GEO/AI visibility audit
- [ ] System generates prioritized recommendations
- [ ] System creates content briefs
- [ ] System drafts safe content with metadata/schema/internal links
- [ ] System generates a clean report
- [ ] System does not auto-publish without approval
- [ ] System is documented well enough for another Hermes agent to continue

---

## First 10 Tickets

1. **Create project documentation and architecture** — All Phase 0 docs
2. **Create database schema** — Businesses, websites, crawls, pages, issues, briefs, drafts, reports, agent logs
3. **Build website intake form/API** — Add business profile
4. **Build safe crawler** — robots.txt, sitemap.xml, homepage, internal pages (25-100 pages)
5. **Build technical SEO analyzer** — Titles, descriptions, headings, canonicals, status codes, internal links, images, schema
6. **Build GEO analyzer** — AI crawler access, entity clarity, llms.txt, citability scoring
7. **Build report generator** — Markdown first, PDF later
8. **Build content brief generator** — Based on business profile + page/topic data
9. **Build schema generator** — Organization, LocalBusiness, WebSite, BreadcrumbList, Service, FAQPage, Article
10. **Build dashboard MVP** — Business selector, crawl status, audit scores, issues, opportunities, reports

---

## Agent Roles

1. **Orchestrator Agent** — Break work into tasks, assign to subagents, maintain project plan, prevent scope drift
2. **Architect Agent** — Design app architecture, DB schema, APIs, folder structure, enforce modularity
3. **SEO Research Agent** — Research SEO/GEO best practices, study inspiration repos, maintain compliance notes
4. **Technical SEO Agent** — Build crawler and audit engine
5. **GEO / AI Visibility Agent** — Build AI crawler checks, llms.txt generator, citability scoring
6. **Content Strategy Agent** — Build keyword/topic engine, content briefs, content calendar
7. **Writing / Editor Agent** — Draft and optimize content, preserve brand voice
8. **Internal Linking Agent** — Build link graph, detect orphan pages, suggest links and anchor text
9. **Integrations Agent** — Connect GSC, GA4, PageSpeed, WordPress, GitHub
10. **QA / Security Agent** — Test all code, validate schema, check rate limits, run tests

---

## Inspiration Repos to Inspect

- **geo-seo-claude** — Use as architecture inspiration for GEO-first SEO workflows, AI crawler checks, citability scoring, schema, content quality, reporting, modular subagents
- **SEO.AI** — Product inspiration only. Extract the idea: autonomous SEO agent that learns a business, plans content, writes/optimizes/publishes, handles internal linking, monitors results
- **marketingskills** — Use as inspiration for modular marketing skills framework

**Rule:** Do not blindly copy implementation. Study architecture and rebuild cleanly. Respect license requirements and preserve attribution if code is reused.

---

## What I've Done

- [x] Received and understood full project specification
- [x] Created project directory at /mnt/c/Users/mtval/Projects/seo-agent-os/
- [x] Created initial AGENT_HANDOFF.md
- [x] Created full folder skeleton: apps/web, services/api, packages/{crawler,seo-audit,geo-audit,content-engine,schema-engine,reporting,integrations,shared}, tests, scripts, storage/{reports,exports,crawl-snapshots}
- [x] Added __init__.py and README.md to each package with documented purpose, structure, key classes/functions, and dependencies
- [x] Wrote docs/ARCHITECTURE.md with full tech stack documentation (Next.js, FastAPI, PostgreSQL, Celery, AI routing, storage, security, compliance)
- [x] Updated AGENT_HANDOFF.md with completed work

## Files Created

- apps/web/__init__.py, apps/web/README.md
- services/api/__init__.py, services/api/README.md
- packages/crawler/__init__.py, packages/crawler/README.md
- packages/seo-audit/__init__.py, packages/seo-audit/README.md
- packages/geo-audit/__init__.py, packages/geo-audit/README.md
- packages/content-engine/__init__.py, packages/content-engine/README.md
- packages/schema-engine/__init__.py, packages/schema-engine/README.md
- packages/reporting/__init__.py, packages/reporting/README.md
- packages/integrations/__init__.py, packages/integrations/README.md
- packages/shared/__init__.py, packages/shared/README.md
- tests/__init__.py, tests/README.md
- scripts/__init__.py, scripts/README.md
- docs/ARCHITECTURE.md

## Commits

- Commit 1: Folder skeleton + package __init__.py + README.md files
- Commit 2: docs/ARCHITECTURE.md (full tech stack documentation)

## What's Next for Flash Agent

**Start with Ticket 1: Create project documentation and architecture**

Produce ALL Phase 0 docs:
1. `docs/PROJECT_BRIEF.md` — Full project brief from the spec
2. `docs/ARCHITECTURE.md` — App architecture decision (Next.js + FastAPI)
3. `docs/AGENT_ROLES.md` — Define all 10 agent roles with responsibilities
4. `docs/ROADMAP.md` — Phased roadmap with MVP definition
5. `docs/DATA_MODEL.md` — Full DB schema for all entities
6. `docs/API_SPEC.md` — REST API endpoints for all MVP commands
7. `docs/SEO_AUDIT_SCORING.md` — Technical SEO scoring model
8. `docs/GEO_AUDIT_SCORING.md` — GEO score model
9. `docs/CONTENT_WORKFLOW.md` — Content generation and optimization workflow
10. `docs/PUBLISHING_SAFETY.md` — Safety protocols for publishing
11. `docs/COMPLIANCE_GUARDRAILS.md` — All 8 guardrails, YMYL rules, cannabis compliance
12. `docs/DECISIONS.md` — Log key architectural decisions
13. `README.md` — Project overview and local setup
14. `.env.example` — Environment variable template

After Phase 0 docs, proceed to:
- Ticket 2: Database schema (use SQLAlchemy/PostgreSQL, Alembic migrations)
- Ticket 3: Website intake API
- Ticket 4: Safe crawler
- Ticket 5: Technical SEO analyzer

---

## Handoff Protocol

1. After each work session, update this AGENT_HANDOFF.md with:
   - What was completed
   - Current status
   - What needs to be done next
   - Key decisions made
   - Files changed
2. Commit changes with meaningful commit messages
3. If an agent needs clarification, ask before proceeding
4. Small, commit-ready changes preferred over large, uncontrolled batches

---

## Notes

- WSL path mapping: `/mnt/c/Users/mtval/Projects/seo-agent-os`
- Worktree rule: never commit to main, never merge into main, never push to GitHub unless explicitly told
- This project has no remote configured yet
