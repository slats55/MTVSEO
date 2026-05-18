# Router: /seo-issues

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from services.api.database import get_db
from services.api.models import SeoIssue, Page, CrawlRun
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
    Includes website_id derived from page -> crawl_run -> website.
    """
    query = select(SeoIssue).options(
        joinedload(SeoIssue.page).joinedload(Page.crawl_run).joinedload(CrawlRun.website)
    )
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
    rows = result.scalars().unique().all()

    items = []
    for seo_issue in rows:
        website_id = UUID("00000000-0000-0000-0000-000000000000")  # default; safest fallback
        try:
            if seo_issue.page and seo_issue.page.crawl_run and seo_issue.page.crawl_run.website:
                website_id = seo_issue.page.crawl_run.website.id
        except Exception:
            pass
        items.append(
            SeoIssueRead(
                id=seo_issue.id,
                page_id=seo_issue.page_id,
                crawl_run_id=seo_issue.crawl_run_id,
                website_id=website_id,
                issue_type=seo_issue.issue_type,
                severity=seo_issue.severity.value if hasattr(seo_issue.severity, "value") else seo_issue.severity,
                title=seo_issue.title,
                description=seo_issue.description,
                recommendation=seo_issue.recommendation,
                affected_element=seo_issue.affected_element,
                created_at=seo_issue.created_at,
                updated_at=seo_issue.updated_at,
            )
        )

    return SeoIssueList(items=items, total=total or 0)


@router.get("/seo-issues/{seo_issue_id}", response_model=SeoIssueRead, status_code=status.HTTP_200_OK)
async def get_seo_issue(
    seo_issue_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> SeoIssueRead:
    """
    Get a single SEO issue by ID.
    Includes website_id derived from page -> crawl_run -> website.
    """
    result = await db.execute(
        select(SeoIssue)
        .options(
            joinedload(SeoIssue.page).joinedload(Page.crawl_run).joinedload(CrawlRun.website)
        )
        .where(SeoIssue.id == seo_issue_id)
    )
    seo_issue = result.scalars().first()
    if not seo_issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"SeoIssue with id={seo_issue_id} not found",
        )

    website_id = UUID("00000000-0000-0000-0000-000000000000")
    try:
        if seo_issue.page and seo_issue.page.crawl_run and seo_issue.page.crawl_run.website:
            website_id = seo_issue.page.crawl_run.website.id
    except Exception:
        pass

    return SeoIssueRead(
        id=seo_issue.id,
        page_id=seo_issue.page_id,
        crawl_run_id=seo_issue.crawl_run_id,
        website_id=website_id,
        issue_type=seo_issue.issue_type,
        severity=seo_issue.severity.value if hasattr(seo_issue.severity, "value") else seo_issue.severity,
        title=seo_issue.title,
        description=seo_issue.description,
        recommendation=seo_issue.recommendation,
        affected_element=seo_issue.affected_element,
        created_at=seo_issue.created_at,
        updated_at=seo_issue.updated_at,
    )