"""Initial migration — create all tables

Revision ID: 20260505_1200
Revises:
Create Date: 2026-05-05 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "20260505_1200"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# ─── ENUM types ───────────────────────────────────────────────────────────────


user_role = postgresql.ENUM(
    "ADMIN", "EDITOR", "VIEWER", name="userrole", create_type=False
)
crawl_status = postgresql.ENUM(
    "PENDING", "RUNNING", "COMPLETED", "FAILED", "CANCELLED",
    name="crawlstatus", create_type=False
)
issue_severity = postgresql.ENUM(
    "CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO",
    name="issueseverity", create_type=False
)
keyword_intent = postgresql.ENUM(
    "INFORMATIONAL", "NAVIGATIONAL", "COMMERCIAL", "TRANSACTIONAL",
    name="keywordintent", create_type=False
)
brief_status = postgresql.ENUM(
    "DRAFT", "APPROVED", "IN_PROGRESS", "PUBLISHED", "ARCHIVED",
    name="briefstatus", create_type=False
)
draft_status = postgresql.ENUM(
    "DRAFT", "PENDING_REVIEW", "APPROVED", "REJECTED", "PUBLISHED",
    name="draftstatus", create_type=False
)
schema_status = postgresql.ENUM(
    "DRAFT", "APPROVED", "ACTIVE",
    name="schemastatus", create_type=False
)
publish_destination = postgresql.ENUM(
    "WORDPRESS", "GITHUB", "MANUAL",
    name="publishdestination", create_type=False
)
publish_status = postgresql.ENUM(
    "PENDING_REVIEW", "APPROVED", "REJECTED", "SUBMITTED", "PUBLISHED", "FAILED",
    name="publishstatus", create_type=False
)
report_type = postgresql.ENUM(
    "FULL_AUDIT", "SEO_AUDIT", "GEO_AUDIT", "CONTENT_AUDIT", "EXECUTIVE_SUMMARY",
    name="reporttype", create_type=False
)
link_type = postgresql.ENUM(
    "INTERNAL", "EXTERNAL",
    name="linktype", create_type=False
)
agent_task_status = postgresql.ENUM(
    "PENDING", "RUNNING", "COMPLETED", "FAILED", "CANCELLED",
    name="agenttaskstatus", create_type=False
)
log_level = postgresql.ENUM(
    "DEBUG", "INFO", "WARNING", "ERROR",
    name="loglevel", create_type=False
)


def upgrade() -> None:
    # ── Create ENUM types first ──────────────────────────────────────────────
    user_role.create(op.get_bind(), checkfirst=True)
    crawl_status.create(op.get_bind(), checkfirst=True)
    issue_severity.create(op.get_bind(), checkfirst=True)
    keyword_intent.create(op.get_bind(), checkfirst=True)
    brief_status.create(op.get_bind(), checkfirst=True)
    draft_status.create(op.get_bind(), checkfirst=True)
    schema_status.create(op.get_bind(), checkfirst=True)
    publish_destination.create(op.get_bind(), checkfirst=True)
    publish_status.create(op.get_bind(), checkfirst=True)
    report_type.create(op.get_bind(), checkfirst=True)
    link_type.create(op.get_bind(), checkfirst=True)
    agent_task_status.create(op.get_bind(), checkfirst=True)
    log_level.create(op.get_bind(), checkfirst=True)

    # ── users ────────────────────────────────────────────────────────────────
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column(
            "role", postgresql.ENUM("ADMIN", "EDITOR", "VIEWER", name="userrole",
                                    create_type=False), nullable=False, default="VIEWER"
        ),
        sa.Column("is_active", sa.Boolean(), nullable=False, default=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    # ── businesses ───────────────────────────────────────────────────────────
    op.create_table(
        "businesses",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("website_url", sa.String(500)),
        sa.Column("description", sa.Text()),
        sa.Column("business_type", sa.String(100)),
        sa.Column("location", sa.String(500)),
        sa.Column("phone", sa.String(50)),
        sa.Column("email", sa.String(255)),
        sa.Column("is_cannabis", sa.Boolean(), nullable=False, default=False),
        sa.Column("is_ymyl", sa.Boolean(), nullable=False, default=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_businesses_user_id", "businesses", ["user_id"], unique=False
    )
    op.create_foreign_key(
        "fk_businesses_user_id", "businesses", "users",
        ["user_id"], ["id"]
    )

    # ── websites ─────────────────────────────────────────────────────────────
    op.create_table(
        "websites",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("business_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("url", sa.String(500), nullable=False),
        sa.Column("name", sa.String(255)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_websites_business_id", "websites", ["business_id"])
    op.create_foreign_key(
        "fk_websites_business_id", "websites", "businesses",
        ["business_id"], ["id"]
    )

    # ── competitors ──────────────────────────────────────────────────────────
    op.create_table(
        "competitors",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("business_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("url", sa.String(500), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("notes", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_competitors_business_id", "competitors", ["business_id"])
    op.create_foreign_key(
        "fk_competitors_business_id", "competitors", "businesses",
        ["business_id"], ["id"]
    )

    # ── crawl_runs ───────────────────────────────────────────────────────────
    op.create_table(
        "crawl_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("website_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "status", postgresql.ENUM(
                "PENDING", "RUNNING", "COMPLETED", "FAILED", "CANCELLED",
                name="crawlstatus", create_type=False
            ), nullable=False, default="PENDING"
        ),
        sa.Column("started_at", sa.DateTime(timezone=True)),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
        sa.Column("pages_discovered", sa.Integer(), default=0),
        sa.Column("pages_crawled", sa.Integer(), default=0),
        sa.Column("crawl_depth", sa.Integer(), default=3),
        sa.Column("max_pages", sa.Integer(), default=50),
        sa.Column("error_message", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_crawl_runs_website_id", "crawl_runs", ["website_id"])
    op.create_foreign_key(
        "fk_crawl_runs_website_id", "crawl_runs", "websites",
        ["website_id"], ["id"]
    )

    # ── pages ────────────────────────────────────────────────────────────────
    op.create_table(
        "pages",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("crawl_run_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("url", sa.String(2000), nullable=False),
        sa.Column("canonical_url", sa.String(2000)),
        sa.Column("status_code", sa.Integer()),
        sa.Column("title", sa.String(500)),
        sa.Column("meta_description", sa.String(1000)),
        sa.Column("h1", sa.String(500)),
        sa.Column("h2_headings", postgresql.JSONB, default=list),
        sa.Column("word_count", sa.Integer()),
        sa.Column("internal_links_count", sa.Integer(), default=0),
        sa.Column("external_links_count", sa.Integer(), default=0),
        sa.Column("images_count", sa.Integer(), default=0),
        sa.Column("images_without_alt", sa.Integer(), default=0),
        sa.Column("has_schema", sa.Boolean(), default=False),
        sa.Column("schema_types", postgresql.JSONB, default=list),
        sa.Column("is_indexable", sa.Boolean(), default=True),
        sa.Column("is_canonical", sa.Boolean(), default=True),
        sa.Column("is_robots_blocked", sa.Boolean(), default=False),
        sa.Column("crawl_depth", sa.Integer()),
        sa.Column("parent_page_id", postgresql.UUID(as_uuid=True)),
        sa.Column("redirect_url", sa.String(2000)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_pages_crawl_run_id", "pages", ["crawl_run_id"])
    op.create_index("ix_pages_url", "pages", ["url"], unique=False)
    op.create_foreign_key(
        "fk_pages_crawl_run_id", "pages", "crawl_runs",
        ["crawl_run_id"], ["id"]
    )
    op.create_foreign_key(
        "fk_pages_parent_page_id", "pages", "pages",
        ["parent_page_id"], ["id"]
    )

    # ── page_snapshots ───────────────────────────────────────────────────────
    op.create_table(
        "page_snapshots",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("page_id", postgresql.UUID(as_uuid=True), nullable=False, unique=True),
        sa.Column("raw_html", sa.LargeBinary()),
        sa.Column("html_hash", sa.String(64)),
        sa.Column("extracted_text", sa.Text()),
        sa.Column("structured_data", postgresql.JSONB, default=dict),
        sa.Column("http_headers", postgresql.JSONB, default=dict),
        sa.Column("screenshot_path", sa.String(500)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_page_snapshots_page_id", "page_snapshots", ["page_id"])
    op.create_foreign_key(
        "fk_page_snapshots_page_id", "page_snapshots", "pages",
        ["page_id"], ["id"]
    )

    # ── seo_issues ───────────────────────────────────────────────────────────
    op.create_table(
        "seo_issues",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("page_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("crawl_run_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("issue_type", sa.String(100), nullable=False),
        sa.Column(
            "severity", postgresql.ENUM(
                "CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO",
                name="issueseverity", create_type=False
            ), nullable=False
        ),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("recommendation", sa.Text()),
        sa.Column("affected_element", sa.String(500)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_seo_issues_page_id", "seo_issues", ["page_id"])
    op.create_index("ix_seo_issues_crawl_run_id", "seo_issues", ["crawl_run_id"])
    op.create_foreign_key(
        "fk_seo_issues_page_id", "seo_issues", "pages",
        ["page_id"], ["id"]
    )
    op.create_foreign_key(
        "fk_seo_issues_crawl_run_id", "seo_issues", "crawl_runs",
        ["crawl_run_id"], ["id"]
    )

    # ── geo_issues ───────────────────────────────────────────────────────────
    op.create_table(
        "geo_issues",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("page_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("crawl_run_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("issue_type", sa.String(100), nullable=False),
        sa.Column(
            "severity", postgresql.ENUM(
                "CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO",
                name="issueseverity", create_type=False
            ), nullable=False
        ),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("recommendation", sa.Text()),
        sa.Column("score_impact", sa.Float(), default=0.0),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_geo_issues_page_id", "geo_issues", ["page_id"])
    op.create_index("ix_geo_issues_crawl_run_id", "geo_issues", ["crawl_run_id"])
    op.create_foreign_key(
        "fk_geo_issues_page_id", "geo_issues", "pages",
        ["page_id"], ["id"]
    )
    op.create_foreign_key(
        "fk_geo_issues_crawl_run_id", "geo_issues", "crawl_runs",
        ["crawl_run_id"], ["id"]
    )

    # ── keywords ────────────────────────────────────────────────────────────
    op.create_table(
        "keywords",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("website_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("keyword", sa.String(500), nullable=False),
        sa.Column(
            "intent", postgresql.ENUM(
                "INFORMATIONAL", "NAVIGATIONAL", "COMMERCIAL", "TRANSACTIONAL",
                name="keywordintent", create_type=False
            )
        ),
        sa.Column("volume", sa.Integer()),
        sa.Column("difficulty", sa.Float()),
        sa.Column("current_rank", sa.Integer()),
        sa.Column("target_url", sa.String(2000)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_keywords_website_id", "keywords", ["website_id"])
    op.create_foreign_key(
        "fk_keywords_website_id", "keywords", "websites",
        ["website_id"], ["id"]
    )

    # ── topic_clusters ───────────────────────────────────────────────────────
    op.create_table(
        "topic_clusters",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("website_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("pillar_page_url", sa.String(2000)),
        sa.Column("search_volume", sa.Integer()),
        sa.Column("priority", sa.Integer()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_topic_clusters_website_id", "topic_clusters", ["website_id"])
    op.create_foreign_key(
        "fk_topic_clusters_website_id", "topic_clusters", "websites",
        ["website_id"], ["id"]
    )

    # ── content_briefs ───────────────────────────────────────────────────────
    op.create_table(
        "content_briefs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("website_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("keyword_id", postgresql.UUID(as_uuid=True)),
        sa.Column("title", sa.String(500)),
        sa.Column("target_url", sa.String(2000)),
        sa.Column(
            "intent", postgresql.ENUM(
                "INFORMATIONAL", "NAVIGATIONAL", "COMMERCIAL", "TRANSACTIONAL",
                name="keywordintent", create_type=False
            )
        ),
        sa.Column("word_count_target", sa.Integer()),
        sa.Column("key_questions", postgresql.JSONB, default=list),
        sa.Column("key_points", postgresql.JSONB, default=list),
        sa.Column("competitor_urls", postgresql.JSONB, default=list),
        sa.Column("recommended_schema", postgresql.JSONB, default=dict),
        sa.Column("internal_link_targets", postgresql.JSONB, default=dict),
        sa.Column("compliance_flags", postgresql.JSONB, default=dict),
        sa.Column(
            "status", postgresql.ENUM(
                "DRAFT", "APPROVED", "IN_PROGRESS", "PUBLISHED", "ARCHIVED",
                name="briefstatus", create_type=False
            ), nullable=False, default="DRAFT"
        ),
        sa.Column("created_by", postgresql.UUID(as_uuid=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_content_briefs_website_id", "content_briefs", ["website_id"])
    op.create_index("ix_content_briefs_keyword_id", "content_briefs", ["keyword_id"])
    op.create_foreign_key(
        "fk_content_briefs_website_id", "content_briefs", "websites",
        ["website_id"], ["id"]
    )
    op.create_foreign_key(
        "fk_content_briefs_keyword_id", "content_briefs", "keywords",
        ["keyword_id"], ["id"]
    )

    # ── content_drafts ───────────────────────────────────────────────────────
    op.create_table(
        "content_drafts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("content_brief_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(500)),
        sa.Column("slug", sa.String(500)),
        sa.Column("content", sa.Text()),
        sa.Column("content_html", sa.Text()),
        sa.Column("meta_title", sa.String(500)),
        sa.Column("meta_description", sa.String(1000)),
        sa.Column("word_count", sa.Integer()),
        sa.Column("schema_markup", postgresql.JSONB, default=dict),
        sa.Column("internal_links", postgresql.JSONB, default=dict),
        sa.Column("compliance_flags", postgresql.JSONB, default=dict),
        sa.Column("compliance_notes", postgresql.JSONB, default=dict),
        sa.Column("usefulness_score", sa.Float()),
        sa.Column(
            "status", postgresql.ENUM(
                "DRAFT", "PENDING_REVIEW", "APPROVED", "REJECTED", "PUBLISHED",
                name="draftstatus", create_type=False
            ), nullable=False, default="DRAFT"
        ),
        sa.Column("created_by", postgresql.UUID(as_uuid=True)),
        sa.Column("approved_by", postgresql.UUID(as_uuid=True)),
        sa.Column("approved_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_content_drafts_content_brief_id", "content_drafts", ["content_brief_id"])
    op.create_foreign_key(
        "fk_content_drafts_content_brief_id", "content_drafts", "content_briefs",
        ["content_brief_id"], ["id"]
    )

    # ── internal_link_opportunities ──────────────────────────────────────────
    op.create_table(
        "internal_link_opportunities",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("website_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("source_page_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("target_page_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("suggested_anchor_text", sa.String(500)),
        sa.Column(
            "link_type", postgresql.ENUM(
                "INTERNAL", "EXTERNAL",
                name="linktype", create_type=False
            ), nullable=False, default="INTERNAL"
        ),
        sa.Column("priority", sa.Integer()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_internal_link_opportunities_website_id", "internal_link_opportunities", ["website_id"]
    )
    op.create_index(
        "ix_internal_link_opportunities_source_page_id", "internal_link_opportunities", ["source_page_id"]
    )
    op.create_index(
        "ix_internal_link_opportunities_target_page_id", "internal_link_opportunities", ["target_page_id"]
    )
    op.create_foreign_key(
        "fk_internal_link_opportunities_website_id", "internal_link_opportunities", "websites",
        ["website_id"], ["id"]
    )
    op.create_foreign_key(
        "fk_internal_link_opportunities_source_page_id", "internal_link_opportunities", "pages",
        ["source_page_id"], ["id"]
    )
    op.create_foreign_key(
        "fk_internal_link_opportunities_target_page_id", "internal_link_opportunities", "pages",
        ["target_page_id"], ["id"]
    )

    # ── schema_drafts ───────────────────────────────────────────────────────
    op.create_table(
        "schema_drafts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("website_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("page_url", sa.String(2000)),
        sa.Column("schema_type", sa.String(100)),
        sa.Column("schema_data", postgresql.JSONB, default=dict),
        sa.Column("is_valid", sa.Boolean(), default=True),
        sa.Column("validation_errors", postgresql.JSONB, default=dict),
        sa.Column(
            "status", postgresql.ENUM(
                "DRAFT", "APPROVED", "ACTIVE",
                name="schemastatus", create_type=False
            ), nullable=False, default="DRAFT"
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_schema_drafts_website_id", "schema_drafts", ["website_id"])
    op.create_foreign_key(
        "fk_schema_drafts_website_id", "schema_drafts", "websites",
        ["website_id"], ["id"]
    )

    # ── publishing_jobs ─────────────────────────────────────────────────────
    op.create_table(
        "publishing_jobs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("content_draft_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "destination", postgresql.ENUM(
                "WORDPRESS", "GITHUB", "MANUAL",
                name="publishdestination", create_type=False
            ), nullable=False
        ),
        sa.Column("destination_url", sa.String(2000)),
        sa.Column(
            "status", postgresql.ENUM(
                "PENDING_REVIEW", "APPROVED", "REJECTED", "SUBMITTED", "PUBLISHED", "FAILED",
                name="publishstatus", create_type=False
            ), nullable=False, default="PENDING_REVIEW"
        ),
        sa.Column("submitted_by", postgresql.UUID(as_uuid=True)),
        sa.Column("approved_by", postgresql.UUID(as_uuid=True)),
        sa.Column("error_message", sa.Text()),
        sa.Column("published_url", sa.String(2000)),
        sa.Column("submitted_at", sa.DateTime(timezone=True)),
        sa.Column("approved_at", sa.DateTime(timezone=True)),
        sa.Column("published_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_publishing_jobs_content_draft_id", "publishing_jobs", ["content_draft_id"])
    op.create_foreign_key(
        "fk_publishing_jobs_content_draft_id", "publishing_jobs", "content_drafts",
        ["content_draft_id"], ["id"]
    )

    # ── reports ──────────────────────────────────────────────────────────────
    op.create_table(
        "reports",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("business_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "report_type", postgresql.ENUM(
                "FULL_AUDIT", "SEO_AUDIT", "GEO_AUDIT", "CONTENT_AUDIT", "EXECUTIVE_SUMMARY",
                name="reporttype", create_type=False
            ), nullable=False
        ),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("summary", sa.Text()),
        sa.Column("seo_score", sa.Float()),
        sa.Column("geo_score", sa.Float()),
        sa.Column("content_score", sa.Float()),
        sa.Column("seo_issues_count", sa.Integer()),
        sa.Column("geo_issues_count", sa.Integer()),
        sa.Column("top_recommendations", postgresql.JSONB, default=list),
        sa.Column("file_path", sa.String(500)),
        sa.Column("created_by", postgresql.UUID(as_uuid=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_reports_business_id", "reports", ["business_id"])
    op.create_foreign_key(
        "fk_reports_business_id", "reports", "businesses",
        ["business_id"], ["id"]
    )

    # ── metric_snapshots ─────────────────────────────────────────────────────
    op.create_table(
        "metric_snapshots",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("business_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("snapshot_date", sa.Date(), nullable=False),
        sa.Column("seo_score", sa.Float()),
        sa.Column("geo_score", sa.Float()),
        sa.Column("organic_sessions", sa.Integer()),
        sa.Column("organic_impressions", sa.Integer()),
        sa.Column("organic_clicks", sa.Integer()),
        sa.Column("avg_position", sa.Float()),
        sa.Column("core_web_vitals", postgresql.JSONB, default=dict),
        sa.Column("top_keywords", postgresql.JSONB, default=list),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_metric_snapshots_business_id", "metric_snapshots", ["business_id"])
    op.create_foreign_key(
        "fk_metric_snapshots_business_id", "metric_snapshots", "businesses",
        ["business_id"], ["id"]
    )

    # ── agent_tasks ──────────────────────────────────────────────────────────
    op.create_table(
        "agent_tasks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("task_type", sa.String(100), nullable=False),
        sa.Column("business_id", postgresql.UUID(as_uuid=True)),
        sa.Column("website_id", postgresql.UUID(as_uuid=True)),
        sa.Column(
            "status", postgresql.ENUM(
                "PENDING", "RUNNING", "COMPLETED", "FAILED", "CANCELLED",
                name="agenttaskstatus", create_type=False
            ), nullable=False, default="PENDING"
        ),
        sa.Column("input_data", postgresql.JSONB, default=dict),
        sa.Column("result_data", postgresql.JSONB, default=dict),
        sa.Column("error_message", sa.Text()),
        sa.Column("started_at", sa.DateTime(timezone=True)),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
        sa.Column("created_by", postgresql.UUID(as_uuid=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_agent_tasks_business_id", "agent_tasks", ["business_id"])
    op.create_index("ix_agent_tasks_website_id", "agent_tasks", ["website_id"])

    # ── agent_run_logs ──────────────────────────────────────────────────────
    op.create_table(
        "agent_run_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("agent_task_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("step", sa.String(100)),
        sa.Column(
            "log_level", postgresql.ENUM(
                "DEBUG", "INFO", "WARNING", "ERROR",
                name="loglevel", create_type=False
            ), nullable=False, default="INFO"
        ),
        sa.Column("message", sa.Text()),
        sa.Column("duration_ms", sa.Integer()),
        sa.Column("metadata", postgresql.JSONB, default=dict),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_agent_run_logs_agent_task_id", "agent_run_logs", ["agent_task_id"])
    op.create_foreign_key(
        "fk_agent_run_logs_agent_task_id", "agent_run_logs", "agent_tasks",
        ["agent_task_id"], ["id"]
    )


def downgrade() -> None:
    op.drop_table("agent_run_logs")
    op.drop_table("agent_tasks")
    op.drop_table("metric_snapshots")
    op.drop_table("reports")
    op.drop_table("publishing_jobs")
    op.drop_table("schema_drafts")
    op.drop_table("internal_link_opportunities")
    op.drop_table("content_drafts")
    op.drop_table("content_briefs")
    op.drop_table("topic_clusters")
    op.drop_table("keywords")
    op.drop_table("geo_issues")
    op.drop_table("seo_issues")
    op.drop_table("page_snapshots")
    op.drop_table("pages")
    op.drop_table("crawl_runs")
    op.drop_table("competitors")
    op.drop_table("websites")
    op.drop_table("businesses")
    op.drop_table("users")

    # Drop enums (if not referenced elsewhere)
    log_level.drop(op.get_bind(), checkfirst=True)
    agent_task_status.drop(op.get_bind(), checkfirst=True)
    link_type.drop(op.get_bind(), checkfirst=True)
    report_type.drop(op.get_bind(), checkfirst=True)
    publish_status.drop(op.get_bind(), checkfirst=True)
    publish_destination.drop(op.get_bind(), checkfirst=True)
    schema_status.drop(op.get_bind(), checkfirst=True)
    draft_status.drop(op.get_bind(), checkfirst=True)
    brief_status.drop(op.get_bind(), checkfirst=True)
    keyword_intent.drop(op.get_bind(), checkfirst=True)
    issue_severity.drop(op.get_bind(), checkfirst=True)
    crawl_status.drop(op.get_bind(), checkfirst=True)
    user_role.drop(op.get_bind(), checkfirst=True)
