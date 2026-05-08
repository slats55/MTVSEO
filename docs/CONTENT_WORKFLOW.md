# Content Workflow — Autonomous SEO Agent OS

**Status:** Phase 2 — Content Engine Core (Briefing + Planning)

---

## Purpose

Describe how content is produced from business profile → brief → draft → review → publish.

## Current State

- Content brief generator exists (`packages/content-engine/brief_generator.py`)
- Keyword clustering exists (`packages/content-engine/keyword_clusterer.py`)
- Content planner exists (`packages/content-engine/content_planner.py`)
- Content drafting **not implemented**
- Publishing workflow **not implemented**

---

## Phase 2: Content Strategy Core

### Inputs

- Business profile (`BusinessRead`): name, type, location, description
- Audit data: issues and scores from SEO/GEO runs (optional)
- Keywords (raw list)

### Workflow

1. **Keyword Clustering**

   `KeywordClusterer.group_by_intent(keywords) → list[KeywordCluster]`

   Groups keywords by semantic intent.

2. **Content Brief Generation**

   `BriefGenerator.create_brief(business, keyword_cluster) → ContentBrief`

   Produces:
   - Target keyword(s)
   - Article title
   - Outline with sections
   - Internal link candidates (from existing pages)
   - Recommended schema type
   - Compliance flags (YMYL, cannabis)
   - Call to Action suggestion

3. **Content Calendar Planning**

   `ContentPlanner.plan(clusters) → ContentCalendar`

   Prioritizes clusters by:
   - Business value
   - Search intent strength
   - Ranking gap
   - Conversion likelihood
   - Content feasibility
   - Internal link support

**Output:** Markdown content brief (JSON + formatted).

---

## Planned: Phase 3+ — Drafting & Publishing

### Content Drafting

`Writing Agent` takes `ContentBrief` → `ContentDraft`.

Must include:

- On-brand prose (tone guidelines)
- Title and meta description
- Body content (H2/H3 structure)
- Internal links (from brief)
- Schema markup
- Useful content check — no fluff, no fake claims

### Review Cycle

- Human reviews draft in dashboard
- Can approve, request changes, or reject
- Version history retained

### Publishing

- Only after human approval
- Applies to WordPress (draft → publish) or GitHub (merge PR)
- NEVER auto-publish

---

## Compliance in Content

- No fake testimonials/reviews
- No invented credentials
- No fake statistics
- YMYL topics require human sign-off
- Cannabis-adjacent follows platform rules

---

## Open Questions

- Which LLM provider? (MiniMax/Hermes)
- How to store `ContentDraft`? (Database table TODO)
- How to manage internal link anchors? (anchor text suggestions TBD)

---

*Last updated:* 2025-05-07
*Branch:* `feature/backend-phase2`