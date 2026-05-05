# Project Brief — Autonomous SEO Agent OS

## 1. Project Name

**Autonomous SEO Agent OS** (SEO Agent OS)

---

## 2. Mission

Build a production-grade autonomous SEO and GEO (Generative Engine Optimization) agent system that can:

1. Audit websites and understand the business they represent
2. Research SEO and GEO opportunities specific to that business
3. Create comprehensive SEO/GEO strategies
4. Generate and optimize content that serves real customer needs
5. Recommend and implement internal link structures
6. Create structured data (JSON-LD schema) automatically
7. Monitor rankings and performance over time
8. Produce actionable reports for human review
9. Eventually publish approved changes automatically — with safety gates

The system serves Orion's own businesses: **MTV Tech Solutions**, **Country Roads Car Services**, **Green Culture** (cannabis — compliance-first), and future local service businesses, ecommerce, SaaS, or content sites.

---

## 3. Inspirations

### geo-seo-claude (Architecture Reference)
- **Use:** Architecture inspiration for GEO-first SEO workflows
- **What to extract:** AI crawler accessibility checks, citability scoring methodology, structured data patterns, content quality evaluation, modular subagent design, reporting templates
- **Rule:** Study architecture and rebuild cleanly. Do not copy implementation wholesale. Respect license requirements and preserve attribution if code is reused.

### SEO.AI (Product Inspiration)
- **Use:** Product category reference — understand the market positioning and feature set of leading autonomous SEO tools
- **What to extract:** The core idea: an autonomous SEO agent that learns a business, plans content, writes/optimizes/publishes, handles internal linking, and monitors results
- **Rule:** Build original, not cloned. Differentiation over imitation.

### marketingskills (Framework Inspiration)
- **Use:** Modular marketing skills framework
- **What to extract:** Skill composition patterns, how domain knowledge is organized and applied, modular skill loading and chaining
- **Rule:** Adapt the modular pattern to the SEO/GEO domain. Do not import marketing-specific workflows verbatim.

---

## 4. Core Principles (Non-Negotiable)

These principles are enforced at every layer — agentic, architectural, and editorial. No exceptions, no matter the business pressure or timeline.

1. **No fake claims, reviews, testimonials, credentials, awards, or statistics** — All content output must be truthful and verifiable. The system should flag or refuse to generate content that includes unverified claims.
2. **No manipulative SEO tactics** — No doorway pages, spun content, keyword stuffing, hidden text, cloaking, or manipulative link schemes. These are antithetical to sustainable business growth and risk algorithmic penalties.
3. **No auto-publish without approval** — Every content output requires human review and explicit approval before it goes live. The publishing pipeline has mandatory gate stages.
4. **No scraping violating terms** — Use only approved APIs and properly licensed data sources. robots.txt and site terms of service are respected by the crawler.
5. **No overwriting files without safety nets** — Git commits, backups, rollback plans, and clear diffs are required before any file write operation.
6. **Every content output must pass a usefulness check** — Does this answer a real customer question? Is it specific to this business? Does it include real expertise and real proof?
7. **YMYL/regulated topics require human review** — Health, finance, legal, and other high-stakes topics trigger mandatory human review workflows.
8. **Cannabis SEO includes compliance checks** — Any content for cannabis-adjacent businesses must pass law checks, platform rule checks, and age restriction verification before publication.

---

## 5. Build Philosophy

### Build Original, Not Cloned
The system is inspired by existing tools but built from scratch for Orion's specific needs. Every component is designed fresh based on the requirements, not reverse-engineered from a reference implementation.

### Compliance-First Architecture
Compliance is not a checkbox — it is woven into the data model, the agent prompts, the content pipeline, and the publishing gates. No content reaches a public surface without passing compliance checks.

### Modular Package Design
Each capability (crawler, audit engine, content generator, schema engine, reporting) is an independent package. They share types and DB models through a common `shared` package. Packages can be updated, replaced, or disabled without requiring full-system rewrites.

### Human-in-the-Loop by Default
Every significant action — crawl, audit, content generation, schema creation, publishing — produces a human-readable report with clear recommendations. The human remains the decision-maker. The system is an analyst and drafter, not an autonomous publisher.

### Score Everything, Display Context
Raw scores (SEO, GEO, Content Opportunity) are computed and stored, but always displayed with supporting context: what drove the score, what the gaps are, what the recommended actions are. A score without context is misleading.

---

## 6. Tech Stack

### Frontend
- **Framework:** Next.js / React
- **Theme:** Clean dashboard, dark professional theme
- **Purpose:** Business management, crawl status monitoring, audit results, content editor, report viewer

### Backend
- **Framework:** Python FastAPI
- **Reason:** Strong for SEO crawling workloads, AI orchestration, async task queuing, and numerical processing
- **Alternative noted:** Node/Express acceptable for simple endpoints, but Python preferred for AI-heavy workloads

### Database
- **Primary:** PostgreSQL — full relational integrity, JSON support for schema storage, robust indexing
- **MVP fallback:** SQLite — for local development and single-instance deployments only

### Task Queue
- **Python-first:** Celery with Redis broker, or RQ (Redis-based simple queue)
- **Node alternative:** BullMQ (Node/TypeScript) if the integration layer uses Node
- **Reason:** Async crawl jobs, scheduled audits, content generation pipelines

### AI / Model Routing
- **Primary:** Hermes agents using MiniMax (model router approach)
  - Cheap models for extraction tasks (crawling, parsing,批量 SEO metric computation)
  - Strong models for strategy, content generation, editorial review
- **Extensible:** Swap in Anthropic, OpenAI, or local models per task type
- **Routing logic:** Defined in agent prompts and enforced by the orchestrator

### Storage
- Reports: Markdown (primary), PDF (later)
- Content drafts: Markdown with frontmatter
- Audit results: JSON
- Crawl snapshots: JSON + HTML snapshots
- SERP snapshots: JSON
- Screenshots: PNG/WebP

---

## 7. Project Structure

```
seo-agent-os/
  apps/
    web/                   # Next.js/React dashboard
  services/
    api/                   # FastAPI backend
  packages/
    crawler/               # Website crawling (robots.txt, sitemap, page fetching)
    seo-audit/            # Technical SEO analysis engine
    geo-audit/             # GEO/AI visibility analysis engine
    content-engine/        # Content generation and optimization
    schema-engine/         # JSON-LD schema generation
    reporting/             # Report generation (Markdown + PDF)
    integrations/          # GSC, GA4, PageSpeed, WordPress, GitHub connectors
    shared/                # Shared utilities, types, database models
  docs/                    # Project documentation
  scripts/                 # Utility scripts
  tests/                   # Test suite
  storage/
    reports/               # Generated audit and content reports
    exports/               # Export packages (CSV, JSON, ZIP)
    crawl-snapshots/        # HTML snapshots of crawled pages
```

### Package Responsibilities

| Package | Responsibility |
|---|---|
| `crawler/` | Fetch pages respecting robots.txt, parse HTML, extract links/meta/schema |
| `seo-audit/` | Compute SEO scores, identify issues, generate recommendations |
| `geo-audit/` | Score AI visibility, check entity clarity, generate llms.txt |
| `content-engine/` | Generate content briefs, draft content, optimize existing content |
| `schema-engine/` | Generate JSON-LD for Organization, LocalBusiness, WebSite, FAQPage, Article, etc. |
| `reporting/` | Assemble Markdown/PDF reports from audit data and scores |
| `integrations/` | Connect to GSC, GA4, PageSpeed Insights, WordPress, GitHub |
| `shared/` | Common SQLAlchemy models, Pydantic schemas, constants, utilities |

---

## 8. Phase Descriptions

### Phase 0: Research & Setup
- Establish project structure
- Produce all foundational documentation
- Set up development environment
- Configure database migrations
- **Duration:** 1–2 days
- **Definition of Done:** All Phase 0 docs complete, schema migrations runnable, empty project structure deployable

### Phase 1: Data Layer & Ingestion
- SQLAlchemy models for all entities
- Alembic migrations
- Website intake API (FastAPI)
- Safe crawler (robots.txt-aware, sitemap-aware, 25–100 page limit)
- **Duration:** 2–3 days
- **Definition of Done:** Can add a business and crawl its site without errors

### Phase 2: SEO Audit Engine
- Technical SEO analyzer: titles, descriptions, headings, canonicals, status codes, internal links, images, schema
- SEO scoring model implementation
- Prioritized recommendations generator
- **Duration:** 2–3 days
- **Definition of Done:** Crawl produces a full technical SEO report with scores and recommendations

### Phase 3: GEO / AI Visibility Engine
- AI crawler accessibility checks
- Entity clarity scoring
- llms.txt generation
- Citability scoring
- Brand authority signal analysis
- **Duration:** 2–3 days
- **Definition of Done:** GEO audit produces a scored report with llms.txt draft

### Phase 4: Content Engine
- Keyword and topic cluster analysis
- Content brief generator (from business profile + audit data)
- Content drafter with brand voice preservation
- Content optimizer
- **Duration:** 3–4 days
- **Definition of Done:** Can generate a content brief and draft from a URL/topic input

### Phase 5: Schema Engine
- JSON-LD schema generator for Organization, LocalBusiness, WebSite, BreadcrumbList, Service, FAQPage, Article
- Schema validator
- Auto-insertion into content drafts
- **Duration:** 1–2 days
- **Definition of Done:** Schema markup is generated and validated for each content draft

### Phase 6: Internal Linking
- Link graph builder from crawl data
- Orphan page detector
- Internal link opportunity finder
- Anchor text recommendation engine
- **Duration:** 2–3 days
- **Definition of Done:** Produces a ranked list of internal link recommendations with source/target/metric

### Phase 7: Report Generator
- Markdown report assembler
- PDF export (future)
- Executive summary view
- Per-business and per-page drill-down
- **Duration:** 1–2 days
- **Definition of Done:** System generates a readable Markdown audit report with scores, issues, and recommendations

### Phase 8: Dashboard MVP
- Business/website selector
- Crawl job status tracker
- Audit scores display (SEO, GEO)
- Issues and opportunities list
- Report viewer
- **Duration:** 3–4 days
- **Definition of Done:** Dashboard displays all key data from Phases 1–7 in a usable UI

### Phase 9: Integrations
- Google Search Console connector
- Google Analytics 4 connector
- PageSpeed Insights connector
- WordPress connector (draft publishing)
- GitHub connector (code/schema commits)
- **Duration:** 3–4 days
- **Definition of Done:** Can pull GSC/GA4 data and push a content draft to WordPress/GitHub

### Phase 10: Monitoring & Refinement
- Rank tracking integration
- Automated re-audit scheduling
- Performance metric snapshots
- Alerting on score degradation
- **Duration:** 2–3 days
- **Definition of Done:** System can run scheduled re-audits and produce delta reports showing score changes over time

---

## 9. Definition of Done (MVP)

- [ ] Can add a business website (name, URL, business type, location, description)
- [ ] System crawls the site safely (respects robots.txt, uses sitemap, limits depth)
- [ ] System runs a full technical SEO audit and produces a score with prioritized issues
- [ ] System runs a full GEO/AI visibility audit and produces a score with recommendations
- [ ] System generates prioritized recommendations (SEO + GEO)
- [ ] System creates content briefs from business profile and audit data
- [ ] System drafts safe content with metadata, schema markup, and internal link suggestions
- [ ] System generates a clean, readable report in Markdown
- [ ] System does NOT auto-publish without approval (human-in-the-loop enforced)
- [ ] System is documented well enough that another Hermes agent can continue without asking clarifying questions

---

## 10. Required Documents

| Document | Phase | Status |
|---|---|---|
| `docs/AGENT_HANDOFF.md` | 0 | DONE |
| `docs/PROJECT_BRIEF.md` | 0 | THIS FILE |
| `docs/ARCHITECTURE.md` | 0 | NEXT |
| `docs/AGENT_ROLES.md` | 0 | NEXT |
| `docs/ROADMAP.md` | 0 | NEXT |
| `docs/DATA_MODEL.md` | 0 | NEXT |
| `docs/API_SPEC.md` | 0 | NEXT |
| `docs/SEO_AUDIT_SCORING.md` | 0 | NEXT |
| `docs/GEO_AUDIT_SCORING.md` | 0 | NEXT |
| `docs/CONTENT_WORKFLOW.md` | 0 | NEXT |
| `docs/PUBLISHING_SAFETY.md` | 0 | NEXT |
| `docs/COMPLIANCE_GUARDRAILS.md` | 0 | NEXT |
| `docs/DECISIONS.md` | 0 | NEXT |
| `README.md` | 0 | NEXT |
| `.env.example` | 0 | NEXT |

---

## 11. Agent Roles Overview

Ten specialized agents drive the system. The Orchestrator assigns work; specialized agents execute domain-specific tasks.

| # | Role | Responsibility |
|---|---|---|
| 1 | **Orchestrator Agent** | Break work into tasks, assign to subagents, maintain project plan, prevent scope drift |
| 2 | **Architect Agent** | Design application architecture, DB schema, APIs, folder structure, enforce modularity |
| 3 | **SEO Research Agent** | Research SEO/GEO best practices, study inspiration repos, maintain compliance notes |
| 4 | **Technical SEO Agent** | Build and operate the crawler and technical SEO audit engine |
| 5 | **GEO / AI Visibility Agent** | Build and operate the GEO audit engine, llms.txt generator, citability scorer |
| 6 | **Content Strategy Agent** | Build keyword/topic engine, content brief generator, content calendar logic |
| 7 | **Writing / Editor Agent** | Draft and optimize content, preserve brand voice, enforce usefulness checks |
| 8 | **Internal Linking Agent** | Build link graph, detect orphan pages, recommend links and anchor text |
| 9 | **Integrations Agent** | Connect to GSC, GA4, PageSpeed, WordPress, GitHub |
| 10 | **QA / Security Agent** | Test all code, validate schema, check rate limits, run compliance validation |

Each role is detailed in `docs/AGENT_ROLES.md`.

---

*Document version: 1.0 — Phase 0*
*Project: Autonomous SEO Agent OS*
*Owner: Orion (MT Val)*