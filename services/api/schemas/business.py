# Pydantic schemas for businesses.

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, HttpUrl


class BusinessBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    website_url: str | None = Field(None, max_length=500)
    description: str | None = None
    business_type: str | None = Field(None, max_length=100)
    location: str | None = Field(None, max_length=500)
    phone: str | None = Field(None, max_length=50)
    email: EmailStr | None = None
    is_cannabis: bool = Field(default=False)
    is_ymyl: bool = Field(default=False)


class BusinessCreate(BusinessBase):
    pass


class BusinessUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    website_url: str | None = Field(None, max_length=500)
    description: str | None = None
    business_type: str | None = Field(None, max_length=100)
    location: str | None = Field(None, max_length=500)
    phone: str | None = Field(None, max_length=50)
    email: EmailStr | None = None
    is_cannabis: bool | None = None
    is_ymyl: bool | None = None


class BusinessRead(BusinessBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BusinessList(BaseModel):
    items: list[BusinessRead]
    total: int
