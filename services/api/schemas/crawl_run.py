# Pydantic schemas for crawl runs.

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CrawlRunBase(BaseModel):
    crawl_depth: int = Field(default=3, ge=1, le=10)
    max_pages: int = Field(default=50, ge=1, le=500)
    respect_robots: bool = Field(default=True)


class CrawlRunCreate(CrawlRunBase):
    website_id: UUID


class CrawlRunUpdate(BaseModel):
    status: str | None = None


class CrawlRunRead(CrawlRunBase):
    id: UUID
    website_id: UUID
    status: str
    started_at: datetime | None
    completed_at: datetime | None
    pages_discovered: int
    pages_crawled: int
    error_message: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CrawlRunList(BaseModel):
    items: list[CrawlRunRead]
    total: int


class CrawlRunStatus(BaseModel):
    id: UUID
    status: str
    pages_discovered: int
    pages_crawled: int
    error_message: str | None
