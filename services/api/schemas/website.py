# Pydantic schemas for websites.

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl


class WebsiteBase(BaseModel):
    url: str = Field(..., min_length=1, max_length=500)
    name: str | None = Field(None, max_length=255)


class WebsiteCreate(WebsiteBase):
    business_id: UUID


class WebsiteUpdate(BaseModel):
    url: str | None = Field(None, min_length=1, max_length=500)
    name: str | None = Field(None, max_length=255)


class WebsiteRead(WebsiteBase):
    id: UUID
    business_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class WebsiteList(BaseModel):
    items: list[WebsiteRead]
    total: int
