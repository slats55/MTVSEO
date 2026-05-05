# Router: /pages

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from services.api.database import get_db
from services.api.models import Page, CrawlRun
from services.api.schemas.page import PageList, PageRead, PageSummary

router = APIRouter()


@router.get("/", response_model=PageList, status_code=status.HTTP_200_OK)
async def list_pages(
    crawl_run_id: UUID | None = None,
    is_indexable: bool | None = None,
    has_schema: bool | None = None,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
) -> PageList:
    """
    List pages, optionally filtered by crawl_run_id and other attributes.
    """
    query = select(Page)
    count_query = select(func.count(Page.id))

    if crawl_run_id:
        query = query.where(Page.crawl_run_id == crawl_run_id)
        count_query = count_query.where(Page.crawl_run_id == crawl_run_id)
    if is_indexable is not None:
        query = query.where(Page.is_indexable == is_indexable)
        count_query = count_query.where(Page.is_indexable == is_indexable)
    if has_schema is not None:
        query = query.where(Page.has_schema == has_schema)
        count_query = count_query.where(Page.has_schema == has_schema)

    total = await db.scalar(count_query)

    result = await db.execute(
        query.order_by(Page.created_at.desc()).offset(skip).limit(limit)
    )
    items = list(result.scalars().all())

    return PageList(items=items, total=total or 0, page=skip // limit + 1, page_size=limit)


@router.get("/{page_id}", response_model=PageRead, status_code=status.HTTP_200_OK)
async def get_page(
    page_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> PageRead:
    """
    Get a single page by ID.
    """
    page = await db.get(Page, page_id)
    if not page:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Page with id={page_id} not found",
        )
    return page


@router.get("/summary/{page_id}", response_model=PageSummary, status_code=status.HTTP_200_OK)
async def get_page_summary(
    page_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> PageSummary:
    """
    Get a lightweight summary of a page (useful for list views).
    """
    page = await db.get(Page, page_id, with_for_update=False)
    if not page:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Page with id={page_id} not found",
        )
    return PageSummary(
        id=page.id,
        url=page.url,
        status_code=page.status_code,
        title=page.title,
        has_schema=page.has_schema,
        is_indexable=page.is_indexable,
        word_count=page.word_count,
    )


@router.get("/by-url/", response_model=PageRead, status_code=status.HTTP_200_OK)
async def get_page_by_url(
    url: str,
    crawl_run_id: UUID = Query(..., description="Crawl run to search within"),
    db: AsyncSession = Depends(get_db),
) -> PageRead:
    """
    Get a page by URL within a specific crawl run.
    """
    result = await db.execute(
        select(Page).where(Page.crawl_run_id == crawl_run_id, Page.url == url).limit(1)
    )
    page = result.scalar_one_or_none()
    if not page:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Page with url={url} not found in crawl run {crawl_run_id}",
        )
    return page
