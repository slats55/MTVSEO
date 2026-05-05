# Autonomous SEO Agent OS

A production-grade autonomous SEO and GEO (Generative Engine Optimization) agent system. This system audits websites, understands businesses, researches opportunities, creates strategies, generates and optimizes content, recommends internal links, creates structured data, monitors performance, and produces actionable reports — with a human-in-the-loop publishing model.

Built for Orion's own businesses: **MTV Tech Solutions**, **Country Roads Car Services**, **Green Culture**, and future ventures.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Project Structure](#project-structure)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Documentation](#documentation)
- [Agent Roles](#agent-roles)
- [Compliance](#compliance)
- [Roadmap](#roadmap)
- [Contributing](#contributing)

---

## Overview

SEO Agent OS automates the full lifecycle of SEO and GEO work — from initial website audit through ongoing content optimization and performance monitoring. The system is designed to be:

- **Honest** — Never generates fake claims, reviews, or statistics
- **Safe** — Never auto-publishes. Every output goes to human review first
- **Compliant** — Built with regulatory guardrails from day one, especially for YMYL and cannabis-adjacent businesses
- **Transparent** — Every score has context; every recommendation has rationale

---

## Features

### Core Capabilities

- **Website Crawling** — robots.txt-aware, sitemap-guided crawling of 25–100 pages per run
- **Technical SEO Audit** — Titles, descriptions, headings, canonicals, status codes, internal links, images, structured data
- **GEO / AI Visibility Audit** — AI crawler accessibility, entity clarity, llms.txt generation, citability scoring
- **SEO Scoring** — 0–100 score with weighted categories and sub-scores
- **GEO Scoring** — 0–100 score measuring AI system visibility and citability
- **Content Brief Generator** — Creates structured content briefs from business profile + audit data
- **Content Drafter** — Generates on-brand content with metadata and schema markup
- **Content Optimizer** — Improves existing content for target keywords and intent
- **Schema Generator** — JSON-LD for Organization, LocalBusiness, WebSite, FAQPage, Article, BreadcrumbList, Service
- **Internal Link Recommender** — Link graph analysis, orphan page detection, anchor text recommendations
- **Report Generator** — Markdown reports with scores, issues, and prioritized recommendations

### Integrations (Phase 9)

- Google Search Console
- Google Analytics 4
- PageSpeed Insights
- WordPress (draft publishing)
- GitHub (code/schema commits)

---

## Project Structure

```
seo-agent-os/
  apps/
    web/                   # Next.js/React dashboard
  services/
    api/                   # FastAPI backend
  packages/
    crawler/               # Website crawling
    seo-audit/             # Technical SEO analysis
    geo-audit/             # GEO/AI visibility analysis
    content-engine/        # Content generation
    schema-engine/         # JSON-LD schema generation
    reporting/              # Report generation
    integrations/          # GSC, GA4, PageSpeed, WordPress, GitHub
    shared/                # Shared types, models, utilities
  docs/                    # Phase 0+ documentation
  scripts/                 # Utility scripts
  tests/                   # Test suite
  storage/
    reports/               # Generated reports
    exports/               # Export packages
    crawl-snapshots/        # HTML snapshots
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js / React |
| Backend | Python FastAPI |
| Database | PostgreSQL (primary), SQLite (MVP) |
| Task Queue | Celery + Redis, or RQ |
| AI | MiniMax via Hermes (model router) |
| Migrations | Alembic |
| ORM | SQLAlchemy |
| Validation | Pydantic |

---

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+ (for dashboard)
- PostgreSQL 14+ (or Docker)
- Redis 6+ (for Celery/RQ)
- Git

### Clone the Repository

```bash
git clone https://github.com/your-org/seo-agent-os.git
cd seo-agent-os
```

### Set Up the Environment

```bash
# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/macOS/WSL
# .venv\Scripts\activate   # Windows

# Install backend dependencies
pip install -r services/api/requirements.txt

# Install frontend dependencies
cd apps/web && npm install && cd ../..
```

### Configure Environment Variables

```bash
cp .env.example .env
# Edit .env with your actual credentials
```

Required environment variables:

```
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/seo_agent_os
SYNC_DATABASE_URL=postgresql://user:pass@localhost:5432/seo_agent_os

# Redis (for Celery/RQ)
REDIS_URL=redis://localhost:6379/0

# AI / Hermes
HERMES_API_KEY=your_hermes_api_key
HERMES_ENDPOINT=http://localhost:8080

# External APIs
GOOGLE_API_KEY=your_google_api_key
GOOGLE_SEARCH_CONSOLE_CLIENT_ID=your_gsc_client_id
GOOGLE_SEARCH_CONSOLE_CLIENT_SECRET=your_gsc_client_secret
OPENAI_API_KEY=your_openai_api_key  # Optional model override

# App
APP_ENV=development
LOG_LEVEL=INFO
SECRET_KEY=change-me-in-production

# File Storage
STORAGE_PATH=./storage
```

### Run Database Migrations

```bash
cd services/api
alembic upgrade head
```

### Start the Backend

```bash
cd services/api
# In one terminal - start the API server
uvicorn main:app --reload --port 8000

# In another terminal - start Celery worker (if using Celery)
celery -A app.worker worker --loglevel=info
```

### Start the Dashboard

```bash
cd apps/web
npm run dev
```

Dashboard available at `http://localhost:3000`
API available at `http://localhost:8000`

### Run Tests

```bash
# Backend tests
cd services/api && pytest

# Frontend tests
cd apps/web && npm test
```

---

## Documentation

All documentation lives in `docs/`. Start here:

| Document | Purpose |
|---|---|
| `docs/PROJECT_BRIEF.md` | Full project specification, mission, tech stack, phases |
| `docs/ARCHITECTURE.md` | System architecture decisions and rationale |
| `docs/AGENT_ROLES.md` | Detailed descriptions of all 10 agent roles |
| `docs/ROADMAP.md` | Phased roadmap with MVP definition and timeline |
| `docs/DATA_MODEL.md` | Complete database schema for all entities |
| `docs/API_SPEC.md` | REST API endpoints for all MVP commands |
| `docs/SEO_AUDIT_SCORING.md` | Technical SEO scoring model details |
| `docs/GEO_AUDIT_SCORING.md` | GEO/AI visibility scoring model details |
| `docs/CONTENT_WORKFLOW.md` | Content generation and optimization workflow |
| `docs/PUBLISHING_SAFETY.md` | Safety protocols for publishing workflows |
| `docs/COMPLIANCE_GUARDRAILS.md` | All compliance guardrails, YMYL rules, cannabis rules |
| `docs/DECISIONS.md` | Key architectural decisions and their rationale |
| `AGENT_HANDOFF.md` | Agent continuity document (for Hermes agents) |

---

## Agent Roles

The system is operated by 10 specialized agents:

| # | Agent | What It Does |
|---|---|---|
| 1 | **Orchestrator** | Breaks work into tasks, assigns to subagents, maintains plan |
| 2 | **Architect** | Designs DB schema, APIs, folder structure |
| 3 | **SEO Research** | Researches best practices, maintains compliance notes |
| 4 | **Technical SEO** | Builds and runs crawler + technical audit engine |
| 5 | **GEO / AI Visibility** | Builds and runs GEO audit engine |
| 6 | **Content Strategy** | Builds keyword/topic engine, content brief generator |
| 7 | **Writing / Editor** | Drafts content, preserves brand voice |
| 8 | **Internal Linking** | Builds link graph, recommends links |
| 9 | **Integrations** | Connects GSC, GA4, WordPress, GitHub |
| 10 | **QA / Security** | Tests code, validates schema, enforces rate limits |

See `docs/AGENT_ROLES.md` for full role descriptions.

---

## Compliance

SEO Agent OS is built on non-negotiable principles:

- **No fake content** — No invented reviews, testimonials, credentials, awards, or statistics
- **No black-hat tactics** — No keyword stuffing, doorway pages, cloaking, link schemes
- **No auto-publish** — Human approval required before any content goes live
- **Terms-compliant scraping** — robots.txt and site terms always respected
- **YMYL human review** — Health, finance, legal topics require mandatory human review
- **Cannabis compliance** — Legal checks, platform rule checks, age verification

See `docs/COMPLIANCE_GUARDRAILS.md` for the full guardrail specification.

---

## Roadmap

See `docs/ROADMAP.md` for full phased roadmap. Summary:

- **Phase 0** — Research & Setup (this phase)
- **Phase 1** — Data Layer & Ingestion (DB schema, crawler, intake API)
- **Phase 2** — SEO Audit Engine
- **Phase 3** — GEO / AI Visibility Engine
- **Phase 4** — Content Engine
- **Phase 5** — Schema Engine
- **Phase 6** — Internal Linking
- **Phase 7** — Report Generator
- **Phase 8** — Dashboard MVP
- **Phase 9** — Integrations
- **Phase 10** — Monitoring & Refinement

---

## Contributing

This project is for Orion's businesses. All work is committed to a worktree branch (`feature/minimax-agent`). Direct commits to `main` are prohibited. Push to GitHub is prohibited unless explicitly authorized.

If continuing this work:
1. Read `AGENT_HANDOFF.md` first
2. Read the relevant Phase 0 doc for the area you're working on
3. Check the current branch with `git branch`
4. Run all tests before committing
5. Update `AGENT_HANDOFF.md` with completed work before ending your session

---

*Project: Autonomous SEO Agent OS*
*Owner: Orion (MT Val)*
*Status: Phase 0 — Research & Setup*