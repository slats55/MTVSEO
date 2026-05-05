# Enums used across all SQLAlchemy models.
# Each enum class maps to a PostgreSQL ENUM type via SQLAlchemy's Enum().

import enum


# ─── User ────────────────────────────────────────────────────────────────────


class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    EDITOR = "EDITOR"
    VIEWER = "VIEWER"


# ─── Crawl ───────────────────────────────────────────────────────────────────


class CrawlStatus(str, enum.Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


# ─── SEO / GEO Issues ────────────────────────────────────────────────────────


class IssueSeverity(str, enum.Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


# ─── Keywords / Content ──────────────────────────────────────────────────────


class KeywordIntent(str, enum.Enum):
    INFORMATIONAL = "INFORMATIONAL"
    NAVIGATIONAL = "NAVIGATIONAL"
    COMMERCIAL = "COMMERCIAL"
    TRANSACTIONAL = "TRANSACTIONAL"


class BriefStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    APPROVED = "APPROVED"
    IN_PROGRESS = "IN_PROGRESS"
    PUBLISHED = "PUBLISHED"
    ARCHIVED = "ARCHIVED"


class DraftStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    PENDING_REVIEW = "PENDING_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    PUBLISHED = "PUBLISHED"


# ─── Schema ───────────────────────────────────────────────────────────────────


class SchemaStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    APPROVED = "APPROVED"
    ACTIVE = "ACTIVE"


# ─── Publishing ──────────────────────────────────────────────────────────────


class PublishDestination(str, enum.Enum):
    WORDPRESS = "WORDPRESS"
    GITHUB = "GITHUB"
    MANUAL = "MANUAL"


class PublishStatus(str, enum.Enum):
    PENDING_REVIEW = "PENDING_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    SUBMITTED = "SUBMITTED"
    PUBLISHED = "PUBLISHED"
    FAILED = "FAILED"


# ─── Reports ─────────────────────────────────────────────────────────────────


class ReportType(str, enum.Enum):
    FULL_AUDIT = "FULL_AUDIT"
    SEO_AUDIT = "SEO_AUDIT"
    GEO_AUDIT = "GEO_AUDIT"
    CONTENT_AUDIT = "CONTENT_AUDIT"
    EXECUTIVE_SUMMARY = "EXECUTIVE_SUMMARY"


# ─── Internal Links ──────────────────────────────────────────────────────────


class LinkType(str, enum.Enum):
    INTERNAL = "INTERNAL"
    EXTERNAL = "EXTERNAL"


# ─── Agent Tasks ─────────────────────────────────────────────────────────────


class AgentTaskStatus(str, enum.Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


# ─── Logging ──────────────────────────────────────────────────────────────────


class LogLevel(str, enum.Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
