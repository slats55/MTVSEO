# SEO Agent OS — Content Engine Package

Generates SEO content briefs with target audience, search intent, keyword strategy, internal link targets, proof sources, CTA, schema type, and business-specific facts.

---

## Architecture

```
packages/content_engine/
  models.py              # All dataclass models: ContentBrief, KeywordSpec, KeywordCluster, etc.
  brief_generator.py     # BriefGenerator — creates full ContentBrief from keyword + business profile
  keyword_clusterer.py   # KeywordClusterer — groups keywords by semantic overlap + intent
  content_planner.py      # ContentPlanner — builds prioritized content calendar from clusters
  __init__.py           # Public API re-exports
  __main__.py           # CLI entry point
  README.md             # This file
```

---

## Public API

```python
from packages.content_engine import (
    # Models
    BusinessContext,
    ContentBrief,
    ContentGoal,
    ContentFormat,
    InternalLinkOpportunity,
    KeywordCluster,
    KeywordSpec,
    OutlineSpec,
    ProofSource,
    SearchIntent,
    SectionSpec,
    Tone,
    # Generators
    BriefGenerator,
    KeywordClusterer,
    ContentPlanner,
)
```

---

## Usage

### Generate a content brief

```python
from packages.content_engine import BriefGenerator, BusinessContext, SearchIntent, ContentFormat

biz = BusinessContext(
    business_name="Mountain View HVAC",
    location="Roanoke, Virginia",
    services=["HVAC repair", "AC installation"],
    unique_selling_points=["24/7 emergency service", "licensed & insured"],
)

generator = BriefGenerator()
brief = generator.run(
    primary_keyword="HVAC repair service",
    business_context=biz,
    secondary_keywords=["AC repair near me", "emergency HVAC"],
    search_intent=SearchIntent.COMMERCIAL,
    content_format=ContentFormat.SERVICE_PAGE,
)
print(brief.slug, brief.outline.total_word_count_target)
```

### Cluster keywords

```python
from packages.content_engine import KeywordClusterer, KeywordSpec, SearchIntent

keywords = [
    KeywordSpec(keyword="HVAC repair", intent=SearchIntent.COMMERCIAL, is_primary=True),
    KeywordSpec(keyword="AC repair near me", intent=SearchIntent.COMMERCIAL),
    KeywordSpec(keyword="furnace maintenance", intent=SearchIntent.INFORMATIONAL),
]
clusters = KeywordClusterer().run(keywords)
for c in clusters:
    print(c.pillar_keyword, c.supporting_keywords)
```

### Build a content plan

```python
from packages.content_engine import ContentPlanner, KeywordCluster

clusters = [...]  # from KeywordClusterer
biz = BusinessContext(business_name="My Business", services=[...])
plan = ContentPlanner().run(clusters, biz)
for entry in plan.entries:
    print(entry.month, entry.priority, entry.primary_keyword)
```

### CLI

```bash
python -m packages.content_engine brief "HVAC repair service" \
    --secondary "AC repair near me,emergency HVAC" \
    --intent commercial --format service_page \
    --business-name "Mountain View HVAC" --location "Roanoke, Virginia"

python -m packages.content_engine cluster keywords.json --min-overlap 0.25

python -m packages.content_engine plan clusters.json \
    --business-name "Mountain View HVAC" --services "HVAC repair,AC installation"
```

---

## Content Brief Structure

Each brief includes:

| Field | Description |
|-------|-------------|
| `slug` | URL-safe slug derived from primary keyword |
| `target_audience` | Persona description |
| `primary_keyword` / `secondary_keywords` | SEO targets |
| `keyword_clusters` | Semantic keyword groupings |
| `search_intent` | Informational / Navigational / Commercial / Transactional |
| `outline` | Ordered `SectionSpec[]` with word count targets, purposes, internal link targets, and schema types |
| `external_proof_sources` | Citations to include |
| `internal_link_targets` | Where to link from this content |
| `primary_cta` | Call-to-action text and placement |
| `recommended_schema_type` | JSON-LD schema type to apply (e.g. Service, FAQPage, Article) |
| `business_facts_to_include` | Facts unique to this business to weave in |
| `compliance_flags` | YMYL / regulated-industry warnings |
| `human_review_required` | Boolean — always true for cannabis/financial/health/legal |
| `tone` | Recommended writing tone |
| `word_count_min/max` | Acceptable range |

---

## Dependencies

| Package | Purpose |
|---------|---------|
| `packages/shared` | Types, exceptions |
| `packages/schema-engine` | Schema type recommendations (optional) |
| `packages/seo-audit` | Keyword analysis from audit data (optional) |
