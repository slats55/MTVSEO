# Reporting Package

Audit report assembly and export.

## Overview

Assembles human-readable Markdown reports from audit data and scores. Generates executive summaries, per-page drill-downs, and prioritized recommendation lists. Supports export to PDF (future).

## Report Types

- **Full Audit Report** — Complete SEO + GEO audit with scores, issues, recommendations
- **Executive Summary** — High-level scores and top 5 priorities per business
- **Technical SEO Report** — Detailed technical SEO findings only
- **GEO Report** — AI visibility findings and llms.txt recommendations
- **Content Report** — Content briefs, drafts, and optimization suggestions
- **Implementation Package** — Exportable ZIP of recommendations, schemas, and drafts

## Responsibilities

- Assemble Markdown reports from structured audit data
- Render Markdown to HTML for web viewing
- Generate executive summaries with score breakdowns
- Per-page drill-down sections
- Prioritized recommendations with effort/impact estimates
- PDF export (Phase 7+)
- Report versioning and diffing

## Key Classes / Functions

- `ReportGenerator` — main report orchestrator
- `SeoReportAssembler` — assembles SEO audit sections
- `GeoReportAssembler` — assembles GEO audit sections
- `ExecutiveSummaryGenerator` — creates high-level summaries
- `MarkdownRenderer` — renders Markdown to HTML
- `PdfExporter` — PDF generation (future)

## Dependencies

- markdown (Python Markdown renderer)
- jinja2 (templating)
- packages.shared
