# Pydantic schemas for SEO issues.

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class SeoIssueRead(BaseModel):
    """Schema for reading a single SEO issue."""

    id: UUID
    page_id: UUID | None
    crawl_run_id: UUID
    issue_type: str
    severity: str
    title: str
    description: str | None
    recommendation: str | None
    affected_element: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SeoIssueList(BaseModel):
    """Schema for a paginated list of SEO issues."""

    items: list[SeoIssueRead]
    total: int
