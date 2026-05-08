# Agent Roles — Autonomous SEO Agent OS

**Status:** Phase 2 — Backend Stabilization

---

## Overview

This project uses specialized agents to divide labor. Each agent has a clear scope and responsibilities.

---

## The 10 Roles

### 1. Orchestrator Agent

**Scope:** Workflow coordination

- Maintains the project plan (Milestones → Phases → Tasks)
- Decomposes feature tickets into atomic work items
- Assigns tasks to specialist agents
- Tracks progress and blockers
- Enforces Definition of Done and quality gates
- Prevents scope creep

**Output:** project plan, task board, handoff docs

---

### 2. Architect Agent

**Scope:** System design

- Creates and updates data model (20 entities)
- Designs API endpoints (REST)
- Defines package boundaries
- Makes tech stack choices (DB, queue, storage)
- Enforces modular architecture

**Output:** `docs/DATA_MODEL.md`, `docs/API_SPEC.md`, `docs/ARCHITECTURE.md`

---

### 3. SEO Research Agent

**Scope:** Best practices and standards

- Researches current Google guidelines
- Reviews Search Essentials
- Studies industry benchmarks
- Maintains compliance notes
- Advises on YMYL and E-E-A-T
- Watches Google algorithm updates

**Output:** compliance notes, scoring models, technical rules

---

### 4. Technical SEO Agent

**Scope:** Crawling and Technical Audit

- Builds crawler (robots.txt, sitemap, BFS)
- Analyzes titles, meta, headings, canonicals
- Detects status codes and redirects
- Checks internal linking structure
- Assesses images, performance, accessibility
- Computes technical SEO score

**Packages:** `packages/crawler`, `packages/seo_audit`

**Output:** crawl data, issues list, score report

---

### 5. GEO / AI Visibility Agent

**Scope:** AI crawler and citability optimization

- Checks AI bot directives (GPTBot, ClaudeBot, etc.)
- Drafts or detects llms.txt
- Scores page citability
- Evaluates entity clarity (Organization schema, sameAs)
- Assesses content depth for AI answers
- Computes GEO score (0–100)

**Packages:** `packages/geo_audit`

**Output:** GEO audit report, llms.txt, citability scores

---

### 6. Content Strategy Agent

**Scope:** Keyword and content planning

- Builds keyword clusters by intent
- Creates content briefs from business profile + opportunities
- Prioritizes content calendar
- Suggests internal link targets (pre-draft)
- Recommends schema types per content
- Flags compliance (YMYL, cannabis)

**Packages:** `packages/content-engine`

**Output:** `ContentBrief`, content plan, keyword map

---

### 7. Writing / Editor Agent

**Scope:** Content generation and optimization

- Drafts on-brand content from briefs
- Preserves business voice (tone guidelines)
- Adds metadata (title, description, slug)
- Embeds schema markup
- Includes internal links
- Optimizes existing content for target keywords

**Note:** Content must pass usefulness check (real customer question? business-specific? includes expertise/proof?).

**Output:** `ContentDraft`, optimized `Page` updates

---

### 8. Internal Linking Agent

**Scope:** Link graph and recommendations

- Builds site link graph from crawl data
- Detects orphan pages
- Recommends internal links (source → target, anchor text)
- Suggests hub pages and topic clusters
- Aligns with content strategy

**Packages:** TODO (not yet implemented)

**Output:** `InternalLinkOpportunity` list

---

### 9. Integrations Agent

**Scope:** External APIs

- Connect Google Search Console API
- Connect Google Analytics 4 API
- Connect PageSpeed Insights API
- Connect WordPress (draft publishing only — no auto-publish)
- Connect GitHub (schema commits)

**Constraints:** Never auto-publish. All publishing must be human-approved. Never overwrite without backup.

**Packages:** `packages/integrations` (TODO)

**Output:** API connectors, credentials management

---

### 10. QA / Security Agent

**Scope:** Quality assurance

- Runs backend tests (pytest)
- Validates API responses (OpenAPI schema)
- Checks rate limiting (future)
- Enforces type hints and linting
- Reviews PRs
- Verifies database migrations
- Ensures crawl/audit jobs don't overload servers

**Output:** test results, quality reports, security checks

---

## Handoff Protocol

When passing work to the next agent:

1. Update `AGENT_HANDOFF.md` with:
   - Completed work
   - Current branch
   - Next tasks
   - Key decisions
   - Files changed
2. Run all tests and verification scripts
3. Make small, commit-ready changes
4. Do not merge or push unless instructed

---

## Agent Divisions

- **Phase 2 work:** MiniMax/Hermes (backend integration, workers, API wiring)
- **Verification/docs:** Step Flash (testing, documentation, small fixes)
- **Product direction:** ChatGPT/user (priority, scope, merge decisions)

---

## Current Active Branch

- Base: `feature/backend-phase2`
- Step Flash docs branch: `docs/phase2-documentation-foundation`

---

*Last updated:* 2025-05-07