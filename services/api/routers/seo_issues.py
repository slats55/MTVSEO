# Router: /seo-issues

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from services.api.database import get_db
from services.api.models import SeoIssue
from services.api.schemas.seo_issue import SeoIssueList, SeoIssueRead

router = APIRouter()


@router.get("/seo-issues/", response_model=SeoIssueList, status_code=status.HTTP_200_OK)
async def list_seo_issues(
    page_id: UUID | None = Query(default=None),
    crawl_run_id: UUID | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> SeoIssueList:
    """
    List all SEO issues, optionally filtered by page_id or crawl_run_id.
    """
    query = select(SeoIssue)
    count_query = select(func.count(SeoIssue.id))

    if page_id is not None:
        query = query.where(SeoIssue.page_id == page_id)
        count_query = count_query.where(SeoIssue.page_id == page_id)

    if crawl_run_id is not None:
        query = query.where(SeoIssue.crawl_run_id == crawl_run_id)
        count_query = count_query.where(SeoIssue.crawl_run_id == crawl_run_id)

    total = await db.scalar(count_query)

    result = await db.execute(
        query.order_by(SeoIssue.created_at.desc()).offset(skip).limit(limit)
    )
    items = list(result.scalars().all())

    return SeoIssueList(items=items, total=total or 0)


@router.get("/seo-issues/{seo_issue_id}", response_model=SeoIssueRead, status_code=status.HTTP_200_OK)
async def get_seo_issue(
    seo_issue_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> SeoIssueRead:
    """
    Get a single SEO issue by ID.
    """
    seo_issue = await db.get(SeoIssue, seo_issue_id)
    if not seo_issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"SeoIssue with id={seo_issue_id} not found",
        )
    return seo_issue
