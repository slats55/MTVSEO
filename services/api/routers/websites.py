# Router: /websites

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from packages.shared.exceptions import EntityNotFoundError
from services.api.database import get_db
from services.api.models import Website, Business
from services.api.schemas.website import (
    WebsiteCreate,
    WebsiteList,
    WebsiteRead,
    WebsiteUpdate,
)

router = APIRouter()


@router.get("/", response_model=WebsiteList, status_code=status.HTTP_200_OK)
async def list_websites(
    business_id: UUID | None = None,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> WebsiteList:
    """
    List all websites, optionally filtered by business_id.
    """
    query = select(Website)
    count_query = select(func.count(Website.id))

    if business_id:
        query = query.where(Website.business_id == business_id)
        count_query = count_query.where(Website.business_id == business_id)

    total = await db.scalar(count_query)

    result = await db.execute(
        query.order_by(Website.created_at.desc()).offset(skip).limit(limit)
    )
    items = list(result.scalars().all())

    return WebsiteList(items=items, total=total or 0)


@router.get("/{website_id}", response_model=WebsiteRead, status_code=status.HTTP_200_OK)
async def get_website(
    website_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> WebsiteRead:
    """
    Get a single website by ID.
    """
    website = await db.get(Website, website_id)
    if not website:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Website with id={website_id} not found",
        )
    return website


@router.post("/", response_model=WebsiteRead, status_code=status.HTTP_201_CREATED)
async def create_website(
    data: WebsiteCreate,
    db: AsyncSession = Depends(get_db),
) -> WebsiteRead:
    """
    Create a new website for an existing business.
    """
    # Verify business exists
    business = await db.get(Business, data.business_id)
    if not business:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Business with id={data.business_id} not found",
        )

    website = Website(
        business_id=data.business_id,
        url=data.url,
        name=data.name,
    )
    db.add(website)
    await db.flush()
    await db.refresh(website)
    return website


@router.patch("/{website_id}", response_model=WebsiteRead, status_code=status.HTTP_200_OK)
async def update_website(
    website_id: UUID,
    data: WebsiteUpdate,
    db: AsyncSession = Depends(get_db),
) -> WebsiteRead:
    """
    Update a website (partial update).
    """
    website = await db.get(Website, website_id)
    if not website:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Website with id={website_id} not found",
        )

    update_data = data.model_dump(exclude_unset=True, exclude_none=True)
    for field, value in update_data.items():
        setattr(website, field, value)

    await db.flush()
    await db.refresh(website)
    return website


@router.delete("/{website_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_website(
    website_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> None:
    """
    Delete a website and all associated crawl runs, pages, etc.
    """
    website = await db.get(Website, website_id)
    if not website:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Website with id={website_id} not found",
        )
    await db.delete(website)
    await db.flush()
