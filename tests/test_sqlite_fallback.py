"""Test SQLite fallback — models create without PostgreSQL."""
import os
import sys
import asyncio
import pytest
import sqlalchemy as sa
from pathlib import Path

repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(repo_root))

_db_counter = 0


def _fresh_db():
    global _db_counter
    _db_counter += 1
    return f"test_sqlite_{_db_counter}.db"


def test_sqlite_creates_all_tables():
    """All 20 models create tables in SQLite without errors."""
    from sqlalchemy.ext.asyncio import create_async_engine
    from services.api.models import Base

    db = _fresh_db()
    engine = create_async_engine(f"sqlite+aiosqlite:///{db}", echo=False)

    async def setup():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    asyncio.run(setup())

    async def check():
        async with engine.connect() as conn:
            result = await conn.execute(
                sa.text("SELECT name FROM sqlite_master WHERE type='table'")
            )
            return sorted([row[0] for row in result.fetchall()])

    tables = asyncio.run(check())
    asyncio.run(engine.dispose())

    try:
        expected = [
            "agent_run_logs", "agent_tasks", "businesses", "competitors",
            "content_briefs", "content_drafts", "crawl_runs", "geo_issues",
            "internal_link_opportunities", "keywords", "metric_snapshots",
            "page_snapshots", "pages", "publishing_jobs", "reports",
            "schema_drafts", "seo_issues", "topic_clusters", "users", "websites",
        ]
        assert tables == expected, f"Expected {expected}, got {tables}"
    finally:
        if os.path.exists(db):
            os.remove(db)


def test_sqlite_orm_imports_cleanly():
    """SQLAlchemy models import and ORM metadata is accessible without a DB connection."""
    from services.api.models import Base, Business, Website, CrawlRun, Page

    # Just verify the models are importable and have relationships defined
    assert hasattr(Business, "__tablename__")
    assert hasattr(Website, "__tablename__")
    assert hasattr(CrawlRun, "__tablename__")
    assert hasattr(Page, "__tablename__")
    # Base.metadata.create_all was already verified in the test above
    assert len(Base.metadata.tables) == 20
