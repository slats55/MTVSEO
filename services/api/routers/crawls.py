# Router: /crawls

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from packages.shared import get_logger
from services.api.database import get_db
from services.api.models import CrawlRun, Website, CrawlStatus
from services.api.schemas.crawl_run import (
    CrawlRunCreate,
    CrawlRunList,
    CrawlRunRead,
    CrawlRunStatus,
)

router = APIRouter()
logger = get_logger(__name__)


@router.get("/crawls/", response_model=CrawlRunList, status_code=status.HTTP_200_OK)
async def list_crawl_runs(
    website_id: UUID | None = None,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> CrawlRunList:
    """
    List all crawl runs, optionally filtered by website_id.
    """
    query = select(CrawlRun)
    count_query = select(func.count(CrawlRun.id))

    if website_id:
        query = query.where(CrawlRun.website_id == website_id)
        count_query = count_query.where(CrawlRun.website_id == website_id)

    total = await db.scalar(count_query)

    result = await db.execute(
        query.order_by(CrawlRun.created_at.desc()).offset(skip).limit(limit)
    )
    items = list(result.scalars().all())

    return CrawlRunList(items=items, total=total or 0)


@router.get("/crawls/{crawl_run_id}", response_model=CrawlRunRead, status_code=status.HTTP_200_OK)
async def get_crawl_run(
    crawl_run_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> CrawlRunRead:
    """
    Get a single crawl run by ID.
    """
    crawl_run = await db.get(CrawlRun, crawl_run_id)
    if not crawl_run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"CrawlRun with id={crawl_run_id} not found",
        )
    return crawl_run


@router.post("/crawls/", response_model=CrawlRunRead, status_code=status.HTTP_201_CREATED)
async def trigger_crawl(
    data: CrawlRunCreate,
    db: AsyncSession = Depends(get_db),
) -> CrawlRunRead:
    """
    Trigger a new crawl for a website.

    Creates a CrawlRun record with status=PENDING, then dispatches
    the Celery crawl worker to execute asynchronously.
    """
    # Verify website exists
    website = await db.get(Website, data.website_id)
    if not website:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Website with id={data.website_id} not found",
        )

    crawl_run = CrawlRun(
        website_id=data.website_id,
        status=CrawlStatus.PENDING,
        crawl_depth=data.crawl_depth,
        max_pages=data.max_pages,
    )
    db.add(crawl_run)
    await db.flush()

    # Commit the CrawlRun first so worker can read it
    await db.commit()
    await db.refresh(crawl_run)

    # Dispatch the Celery task (best-effort — log but don't fail the HTTP response)
    try:
        # Import here to avoid circular import; lazy so Celery is only loaded when needed
        from services.api.celery_app import celery_app
        from packages.crawler.crawl_worker import crawl_website_task

        task = crawl_website_task.delay(
            crawl_run_id=str(crawl_run.id),
            start_url=website.url,
            max_pages=data.max_pages,
            crawl_depth=data.crawl_depth,
            respect_robots=data.respect_robots,
        )
        logger.info(
            "Crawl worker dispatched",
            extra={
                "crawl_run_id": str(crawl_run.id),
                "website_id": str(data.website_id),
                "celery_task_id": task.id,
            },
        )
    except Exception as exc:
        # Don't fail the HTTP response — crawl is saved; worker can be re-triggered
        logger.warning(
            "Failed to dispatch crawl worker for CrawlRun %s: %s",
            str(crawl_run.id),
            exc,
        )

    return crawl_run


@router.get("/crawls/{crawl_run_id}/status", response_model=CrawlRunStatus, status_code=status.HTTP_200_OK)
async def get_crawl_run_status(
    crawl_run_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> CrawlRunStatus:
    """
    Get lightweight status info for a crawl run (useful for polling).
    """
    crawl_run = await db.get(CrawlRun, crawl_run_id)
    if not crawl_run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"CrawlRun with id={crawl_run_id} not found",
        )
    return CrawlRunStatus(
        id=crawl_run.id,
        status=crawl_run.status.value,
        pages_discovered=crawl_run.pages_discovered,
        pages_crawled=crawl_run.pages_crawled,
        error_message=crawl_run.error_message,
    )


@router.post("/crawls/{crawl_run_id}/cancel", response_model=CrawlRunRead, status_code=status.HTTP_200_OK)
async def cancel_crawl_run(
    crawl_run_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> CrawlRunRead:
    """
    Cancel a pending or running crawl.
    """
    crawl_run = await db.get(CrawlRun, crawl_run_id)
    if not crawl_run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"CrawlRun with id={crawl_run_id} not found",
        )

    if crawl_run.status in (CrawlStatus.COMPLETED, CrawlStatus.FAILED, CrawlStatus.CANCELLED):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"CrawlRun is already {crawl_run.status.value}",
        )

    crawl_run.status = CrawlStatus.CANCELLED
    await db.flush()
    logger.info("Crawl run cancelled", extra={"crawl_run_id": str(crawl_run_id)})
    return crawl_run
