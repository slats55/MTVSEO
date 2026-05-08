# Router: /businesses

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from packages.shared.exceptions import EntityNotFoundError
from services.api.database import get_db
from services.api.models import Business
from services.api.schemas.business import (
    BusinessCreate,
    BusinessList,
    BusinessRead,
    BusinessUpdate,
)

router = APIRouter()


@router.get("/businesses/", response_model=BusinessList, status_code=status.HTTP_200_OK)
async def list_businesses(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> BusinessList:
    """
    List all businesses with pagination.
    """
    total = await db.scalar(select(func.count(Business.id)))

    result = await db.execute(
        select(Business).order_by(Business.created_at.desc()).offset(skip).limit(limit)
    )
    items = list(result.scalars().all())

    return BusinessList(items=items, total=total or 0)


@router.get("/businesses/{business_id}", response_model=BusinessRead, status_code=status.HTTP_200_OK)
async def get_business(
    business_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> BusinessRead:
    """
    Get a single business by ID.
    """
    business = await db.get(Business, business_id)
    if not business:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Business with id={business_id} not found",
        )
    return business


@router.post("/businesses/", response_model=BusinessRead, status_code=status.HTTP_201_CREATED)
async def create_business(
    data: BusinessCreate,
    db: AsyncSession = Depends(get_db),
) -> BusinessRead:
    """
    Create a new business.
    """
    # TODO: Get user_id from auth context (JWT). Using a placeholder UUID for now.
    user_id = UUID("00000000-0000-0000-0000-000000000000")

    business = Business(
        user_id=user_id,
        name=data.name,
        website_url=data.website_url,
        description=data.description,
        business_type=data.business_type,
        location=data.location,
        phone=data.phone,
        email=data.email,
        is_cannabis=data.is_cannabis,
        is_ymyl=data.is_ymyl,
    )
    db.add(business)
    await db.flush()
    return business


@router.patch("/businesses/{business_id}", response_model=BusinessRead, status_code=status.HTTP_200_OK)
async def update_business(
    business_id: UUID,
    data: BusinessUpdate,
    db: AsyncSession = Depends(get_db),
) -> BusinessRead:
    """
    Update a business (partial update).
    """
    business = await db.get(Business, business_id)
    if not business:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Business with id={business_id} not found",
        )

    update_data = data.model_dump(exclude_unset=True, exclude_none=True)
    for field, value in update_data.items():
        setattr(business, field, value)

    await db.flush()
    return business


@router.delete("/businesses/{business_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_business(
    business_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> None:
    """
    Delete a business and all associated records (cascades).
    """
    business = await db.get(Business, business_id)
    if not business:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Business with id={business_id} not found",
        )
    await db.delete(business)
    await db.flush()
