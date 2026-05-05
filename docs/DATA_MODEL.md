# Data Model — Autonomous SEO Agent OS

## Entity Relationship Overview

```
User
  └── Business (1:N)
        ├── Website (1:N)
        │     ├── CrawlRun (1:N)
        │     │     ├── Page (1:N)
        │     │     │     ├── PageSnapshot (1:1)
        │     │     │     ├── SeoIssue (1:N)
        │     │     │     └── GeoIssue (1:N)
        │     │     └── Keyword (N:N via ContentBrief)
        │     ├── ContentBrief (1:N)
        │     │     └── ContentDraft (1:N)
        │     ├── SchemaDraft (1:N)
        │     └── InternalLinkOpportunity (N:1 Page)
        │     └── PublishingJob (N:1 ContentDraft)
        ├── Competitor (N:N Website)
        └── MetricSnapshot (N:1 Business)
Report (N:1 Business)
AgentTask (N:1 User)
AgentRunLog (N:1 AgentTask)
```

---

## Entity Definitions

### 1. User

Represents a human operator with access to the system.

| Field | Type | Constraints |
|---|---|---|
| id | UUID | PK |
| email | String(255) | Unique, not null |
| name | String(255) | not null |
| password_hash | String(255) | not null |
| role | Enum(UserRole) | default=VIEWER |
| created_at | DateTime | not null, default=now |
| updated_at | DateTime | not null |
| is_active | Boolean | default=True |

**Enums:**
- `UserRole`: ADMIN, EDITOR, VIEWER

---

### 2. Business

Represents a business entity being audited. One user can own multiple businesses.

| Field | Type | Constraints |
|---|---|---|
| id | UUID | PK |
| user_id | UUID | FK → User.id, not null |
| name | String(255) | not null |
| website_url | String(500) | |
| description | Text | |
| business_type | String(100) | e.g. "Auto Rental", "Legal Service", "Cannabis" |
| location | String(500) | City/state/address |
| phone | String(50) | |
| email | String(255) | |
| is_cannabis | Boolean | default=False — triggers cannabis compliance checks |
| is_ymyl | Boolean | default=False — triggers YMYL human-review requirement |
| created_at | DateTime | not null |
| updated_at | DateTime | not null |

---

### 3. Website

Represents a specific website associated with a business.

| Field | Type | Constraints |
|---|---|---|
| id | UUID | PK |
| business_id | UUID | FK → Business.id, not null |
| url | String(500) | not null |
| name | String(255) | e.g. "Main Site", "Blog" |
| created_at | DateTime | not null |
| updated_at | DateTime | not null |

---

### 4. Competitor

Represents a competitor website tracked for comparison.

| Field | Type | Constraints |
|---|---|---|
| id | UUID | PK |
| business_id | UUID | FK → Business.id, not null |
| url | String(500) | not null |
| name | String(255) | not null |
| notes | Text | |
| created_at | DateTime | not null |

---

### 5. CrawlRun

Represents a single crawl job execution.

| Field | Type | Constraints |
|---|---|---|
| id | UUID | PK |
| website_id | UUID | FK → Website.id, not null |
| status | Enum(CrawlStatus) | not null |
| started_at | DateTime | |
| completed_at | DateTime | |
| pages_discovered | Integer | default=0 |
| pages_crawled | Integer | default=0 |
| crawl_depth | Integer | default=3 |
| max_pages | Integer | default=50 |
| error_message | Text | |
| created_at | DateTime | not null |

**Enums:**
- `CrawlStatus`: PENDING, RUNNING, COMPLETED, FAILED, CANCELLED

---

### 6. Page

Represents a single crawled page.

| Field | Type | Constraints |
|---|---|---|
| id | UUID | PK |
| crawl_run_id | UUID | FK → CrawlRun.id, not null |
| url | String(2000) | not null, unique per crawl |
| canonical_url | String(2000) | |
| status_code | Integer | |
| title | String(500) | |
| meta_description | String(1000) | |
| h1 | String(500) | |
| h2_headings | JSON | List of H2 text strings |
| word_count | Integer | |
| internal_links_count | Integer | |
| external_links_count | Integer | |
| images_count | Integer | |
| images_without_alt | Integer | |
| has_schema | Boolean | default=False |
| schema_types | JSON | List of schema @type values |
| is_indexable | Boolean | |
| is_canonical | Boolean | |
| is_robots_blocked | Boolean | |
| crawl_depth | Integer | |
| parent_page_id | UUID | FK → Page.id (self-referential) |
| redirect_url | String(2000) | |
| created_at | DateTime | not null |

---

### 7. PageSnapshot

Raw and structured data snapshot for a crawled page (one-to-one with Page).

| Field | Type | Constraints |
|---|---|---|
| id | UUID | PK |
| page_id | UUID | FK → Page.id, unique, not null |
| raw_html | LargeBinary | |
| html_hash | String(64) | SHA-256 of raw HTML |
| extracted_text | Text | |
| structured_data | JSON | All JSON-LD schemas found |
| http_headers | JSON | Response headers |
| screenshot_path | String(500) | Path to screenshot file |
| created_at | DateTime | not null |

---

### 8. SeoIssue

Represents a single technical SEO issue found on a page.

| Field | Type | Constraints |
|---|---|---|
| id | UUID | PK |
| page_id | UUID | FK → Page.id, not null |
| crawl_run_id | UUID | FK → CrawlRun.id, not null |
| issue_type | String(100) | e.g. "missing_title", "duplicate_h1", "broken_link" |
| severity | Enum(IssueSeverity) | not null |
| title | String(255) | Human-readable issue title |
| description | Text | |
| recommendation | Text | |
| affected_element | String(500) | e.g. URL, selector, element |
| created_at | DateTime | not null |

**Enums:**
- `IssueSeverity`: CRITICAL, HIGH, MEDIUM, LOW, INFO

---

### 9. GeoIssue

Represents a single GEO/AI visibility issue found on a page.

| Field | Type | Constraints |
|---|---|---|
| id | UUID | PK |
| page_id | UUID | FK → Page.id, not null |
| crawl_run_id | UUID | FK → CrawlRun.id, not null |
| issue_type | String(100) | e.g. "ai_crawler_blocked", "no_entity_schema", "low_citability" |
| severity | Enum(IssueSeverity) | not null |
| title | String(255) | Human-readable issue title |
| description | Text | |
| recommendation | Text | |
| score_impact | Float | How much this issue reduces the GEO score |
| created_at | DateTime | not null |

---

### 10. Keyword

Represents a target keyword or key phrase.

| Field | Type | Constraints |
|---|---|---|
| id | UUID | PK |
| website_id | UUID | FK → Website.id, not null |
| keyword | String(500) | not null |
| intent | Enum(KeywordIntent) | |
| volume | Integer | Estimated monthly search volume |
| difficulty | Float | 0–100 difficulty score |
| current_rank | Integer | Current ranking position (if tracked) |
| target_url | String(2000) | Target page URL for this keyword |
| created_at | DateTime | not null |
| updated_at | DateTime | not null |

**Enums:**
- `KeywordIntent`: INFORMATIONAL, NAVIGATIONAL, COMMERCIAL, TRANSACTIONAL

---

### 11. TopicCluster

Groups related keywords around a central topic/pillar page.

| Field | Type | Constraints |
|---|---|---|
| id | UUID | PK |
| website_id | UUID | FK → Website.id, not null |
| name | String(255) | not null |
| pillar_page_url | String(2000) | |
| search_volume | Integer | Total cluster volume |
| priority | Integer | 1–10 priority score |
| created_at | DateTime | not null |

---

### 12. ContentBrief

Represents a generated content brief for a target keyword/topic.

| Field | Type | Constraints |
|---|---|---|
| id | UUID | PK |
| website_id | UUID | FK → Website.id, not null |
| keyword_id | UUID | FK → Keyword.id |
| title | String(500) | Suggested content title |
| target_url | String(2000) | Target page URL |
| intent | Enum(KeywordIntent) | |
| word_count_target | Integer | Target word count |
| key_questions | JSON | List of questions to answer |
| key_points | JSON | Key points to cover |
| competitor_urls | JSON | Reference competitor pages |
| recommended_schema | JSON | Schema types to include |
| internal_link_targets | JSON | Suggested internal link anchors/URLs |
| compliance_flags | JSON | Cannabis/YMYL flags |
| status | Enum(BriefStatus) | not null |
| created_by | UUID | FK → User.id |
| created_at | DateTime | not null |
| updated_at | DateTime | not null |

**Enums:**
- `BriefStatus`: DRAFT, APPROVED, IN_PROGRESS, PUBLISHED, ARCHIVED

---

### 13. ContentDraft

Represents a draft of content generated from a brief.

| Field | Type | Constraints |
|---|---|---|
| id | UUID | PK |
| content_brief_id | UUID | FK → ContentBrief.id, not null |
| title | String(500) | |
| slug | String(500) | URL slug |
| content | Text | Markdown content |
| content_html | Text | Rendered HTML |
| meta_title | String(500) | |
| meta_description | String(1000) | |
| word_count | Integer | |
| schema_markup | JSON | Generated JSON-LD schema |
| internal_links | JSON | Suggested internal links embedded |
| compliance_flags | JSON | Passed/failed compliance checks |
| compliance_notes | JSON | Detailed compliance notes |
| usefulness_score | Float | 0–1 AI-assessed usefulness |
| status | Enum(DraftStatus) | not null |
| created_by | UUID | FK → User.id |
| approved_by | UUID | FK → User.id |
| approved_at | DateTime | |
| created_at | DateTime | not null |
| updated_at | DateTime | not null |

**Enums:**
- `DraftStatus`: DRAFT, PENDING_REVIEW, APPROVED, REJECTED, PUBLISHED

---

### 14. InternalLinkOpportunity

Represents a recommended internal link addition.

| Field | Type | Constraints |
|---|---|---|
| id | UUID | PK |
| website_id | UUID | FK → Website.id, not null |
| source_page_id | UUID | FK → Page.id, not null |
| target_page_id | UUID | FK → Page.id, not null |
| suggested_anchor_text | String(500) | Recommended anchor text |
| link_type | Enum(LinkType) | INTERNAL or EXTERNAL |
| priority | Integer | 1–10 priority |
| created_at | DateTime | not null |

**Enums:**
- `LinkType`: INTERNAL, EXTERNAL

---

### 15. SchemaDraft

Represents a generated JSON-LD schema markup set for a page.

| Field | Type | Constraints |
|---|---|---|
| id | UUID | PK |
| website_id | UUID | FK → Website.id, not null |
| page_url | String(2000) | |
| schema_type | String(100) | Primary schema @type |
| schema_data | JSON | Full JSON-LD object |
| is_valid | Boolean | |
| validation_errors | JSON | Any JSON-LD validation errors |
| status | Enum(SchemaStatus) | not null |
| created_at | DateTime | not null |
| updated_at | DateTime | not null |

**Enums:**
- `SchemaStatus`: DRAFT, APPROVED, ACTIVE

---

### 16. PublishingJob

Represents a content publishing workflow.

| Field | Type | Constraints |
|---|---|---|
| id | UUID | PK |
| content_draft_id | UUID | FK → ContentDraft.id, not null |
| destination | Enum(PublishDestination) | not null |
| destination_url | String(2000) | Target URL/endpoint |
| status | Enum(PublishStatus) | not null |
| submitted_by | UUID | FK → User.id |
| approved_by | UUID | FK → User.id |
| error_message | Text | |
| published_url | String(2000) | Actual published URL |
| submitted_at | DateTime | |
| approved_at | DateTime | |
| published_at | DateTime | |
| created_at | DateTime | not null |

**Enums:**
- `PublishDestination`: WORDPRESS, GITHUB, MANUAL
- `PublishStatus`: PENDING_REVIEW, APPROVED, REJECTED, SUBMITTED, PUBLISHED, FAILED

---

### 17. Report

Represents a generated audit or content report.

| Field | Type | Constraints |
|---|---|---|
| id | UUID | PK |
| business_id | UUID | FK → Business.id, not null |
| report_type | Enum(ReportType) | not null |
| title | String(500) | not null |
| summary | Text | Executive summary |
| seo_score | Float | 0–100 |
| geo_score | Float | 0–100 |
| content_score | Float | 0–100 |
| seo_issues_count | Integer | |
| geo_issues_count | Integer | |
| top_recommendations | JSON | Top 5 recommendations |
| file_path | String(500) | Path to report file (Markdown/PDF) |
| created_by | UUID | FK → User.id |
| created_at | DateTime | not null |

**Enums:**
- `ReportType`: FULL_AUDIT, SEO_AUDIT, GEO_AUDIT, CONTENT_AUDIT, EXECUTIVE_SUMMARY

---

### 18. MetricSnapshot

Represents a point-in-time snapshot of performance metrics for a business.

| Field | Type | Constraints |
|---|---|---|
| id | UUID | PK |
| business_id | UUID | FK → Business.id, not null |
| snapshot_date | Date | not null |
| seo_score | Float | |
| geo_score | Float | |
| organic_sessions | Integer | GA4 organic sessions |
| organic_impressions | Integer | GSC impressions |
| organic_clicks | Integer | GSC clicks |
| avg_position | Float | GSC average ranking position |
| core_web_vitals | JSON | LCP, FID, CLS scores |
| top_keywords | JSON | Top 5 keywords with positions |
| created_at | DateTime | not null |

---

### 19. AgentTask

Represents a task assigned to an AI agent.

| Field | Type | Constraints |
|---|---|---|
| id | UUID | PK |
| task_type | String(100) | e.g. "crawl", "audit_seo", "generate_brief" |
| business_id | UUID | FK → Business.id |
| website_id | UUID | FK → Website.id |
| status | Enum(AgentTaskStatus) | not null |
| input_data | JSON | Task input parameters |
| result_data | JSON | Task output |
| error_message | Text | |
| started_at | DateTime | |
| completed_at | DateTime | |
| created_by | UUID | FK → User.id |
| created_at | DateTime | not null |

**Enums:**
- `AgentTaskStatus`: PENDING, RUNNING, COMPLETED, FAILED, CANCELLED

---

### 20. AgentRunLog

Detailed execution log for an agent task run.

| Field | Type | Constraints |
|---|---|---|
| id | UUID | PK |
| agent_task_id | UUID | FK → AgentTask.id, not null |
| step | String(100) | Logical step name |
| log_level | Enum(LogLevel) | INFO, WARNING, ERROR |
| message | Text | |
| duration_ms | Integer | Step duration in milliseconds |
| metadata | JSON | Additional context |
| created_at | DateTime | not null |

**Enums:**
- `LogLevel`: DEBUG, INFO, WARNING, ERROR

---

*Document version: 1.0 — Phase 1*
*Project: Autonomous SEO Agent OS*
*Owner: Orion (MT Val)*
