# Pydantic schemas for pages.

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class PageBase(BaseModel):
    url: str = Field(..., max_length=2000)


class PageRead(PageBase):
    id: UUID
    crawl_run_id: UUID
    canonical_url: str | None
    status_code: int | None
    title: str | None
    meta_description: str | None
    h1: str | None
    h2_headings: list | None
    word_count: int | None
    internal_links_count: int
    external_links_count: int
    images_count: int
    images_without_alt: int
    has_schema: bool
    schema_types: list | None
    is_indexable: bool
    is_canonical: bool
    is_robots_blocked: bool
    crawl_depth: int | None
    parent_page_id: UUID | None
    redirect_url: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PageList(BaseModel):
    items: list[PageRead]
    total: int
    page: int
    page_size: int


class PageSummary(BaseModel):
    """Lightweight page summary for list views."""
    id: UUID
    url: str
    status_code: int | None
    title: str | None
    has_schema: bool
    is_indexable: bool
    word_count: int | None
