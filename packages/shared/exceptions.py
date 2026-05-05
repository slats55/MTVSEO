# Shared exception classes.
# All packages and services should raise these for uniform error handling.


class SeoAgentException(Exception):
    """Base exception for all SEO Agent OS errors."""

    def __init__(self, message: str, detail: str | None = None):
        super().__init__(message)
        self.message = message
        self.detail = detail


# ─── Crawler errors ───────────────────────────────────────────────────────────


class CrawlerException(SeoAgentException):
    """Raised when crawler encounters a fatal error."""
    pass


class RobotsDisallowedError(CrawlerException):
    """Raised when a URL is blocked by robots.txt."""
    pass


class SitemapNotFoundError(CrawlerException):
    """Raised when sitemap.xml cannot be found at expected location."""
    pass


class CrawlDepthExceededError(CrawlerException):
    """Raised when max crawl depth is reached."""
    pass


class CrawlMaxPagesError(CrawlerException):
    """Raised when max page limit is reached."""
    pass


# ─── Audit errors ─────────────────────────────────────────────────────────────


class AuditException(SeoAgentException):
    """Raised when an audit fails."""
    pass


class AuditTimeoutError(AuditException):
    """Raised when an audit run times out."""
    pass


# ─── Content errors ────────────────────────────────────────────────────────────


class ContentException(SeoAgentException):
    """Raised when content generation or optimization fails."""
    pass


class ComplianceViolationError(ContentException):
    """Raised when content violates compliance rules (YMYL, cannabis, etc.)."""

    def __init__(self, message: str, failed_checks: list[str]):
        super().__init__(message)
        self.failed_checks = failed_checks


class UsefulnessCheckFailedError(ContentException):
    """Raised when generated content fails the usefulness check."""
    pass


# ─── Database errors ──────────────────────────────────────────────────────────


class DatabaseException(SeoAgentException):
    """Raised for database operation failures."""
    pass


class EntityNotFoundError(DatabaseException):
    """Raised when a requested entity does not exist."""

    def __init__(self, entity_name: str, entity_id: str):
        super().__init__(f"{entity_name} with id={entity_id} not found")
        self.entity_name = entity_name
        self.entity_id = entity_id


class DuplicateEntityError(DatabaseException):
    """Raised when creating an entity that already exists."""

    def __init__(self, entity_name: str, field: str, value: str):
        super().__init__(f"{entity_name} with {field}={value} already exists")
        self.entity_name = entity_name
        self.field = field
        self.value = value


# ─── Publishing errors ─────────────────────────────────────────────────────────


class PublishingException(SeoAgentException):
    """Raised when publishing fails."""
    pass


class ApprovalRequiredError(PublishingException):
    """Raised when attempting to publish without approval."""
    pass


class PublishingDestinationError(PublishingException):
    """Raised when publishing to a destination fails (WordPress, GitHub, etc.)."""
    pass


# ─── External API errors ───────────────────────────────────────────────────────


class ExternalApiException(SeoAgentException):
    """Raised when an external API call fails."""

    def __init__(self, service: str, message: str, status_code: int | None = None):
        super().__init__(f"[{service}] {message}")
        self.service = service
        self.status_code = status_code


class RateLimitExceededError(ExternalApiException):
    """Raised when an external API rate limit is hit."""

    def __init__(self, service: str, retry_after: int | None = None):
        retry_msg = f" retry after {retry_after}s" if retry_after else ""
        super().__init__(service, f"Rate limit exceeded{retry_msg}")
        self.retry_after = retry_after


# ─── Validation errors ─────────────────────────────────────────────────────────


class ValidationException(SeoAgentException):
    """Raised for input validation failures."""
    pass


class ConfigurationError(SeoAgentException):
    """Raised when a required configuration value is missing."""
    pass
