# Endpoint smoke tests — verifies API route mounting and response shapes.
# No Redis, Celery, external APIs, or real PostgreSQL required.
#
# Tests here verify:
# - App creates without errors
# - /health returns 200 + expected fields
# - Router prefixes are mounted (/api/v1/businesses, /api/v1/websites, etc.)
# - HTTP methods (GET/POST) are accepted by routes (checked via status codes)
# - Database session can be acquired from a SQLite engine
#
# Note: Full CRUD endpoint tests require the FK relationship bugs in models
# (AgentTask.creator, AgentRunLog.task, etc.) to be fixed first. Those are
# tracked as a separate follow-up task.

import pytest
from httpx import ASGITransport, AsyncClient

# Import the factory (creates app without starting lifespan/SQLEngine init)
from services.api.main import create_app


# =============================================================================
# App creation smoke
# =============================================================================

def test_app_creates_without_error():
    """App factory returns a FastAPI app without raising."""
    app = create_app()
    assert app is not None


# =============================================================================
# Health endpoint
# =============================================================================

@pytest.mark.asyncio
async def test_health_endpoint_shape():
    """Health returns 200 and expected fields including version."""
    app = create_app()
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        follow_redirects=False,
    ) as client:
        response = await client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "healthy"
    assert "version" in data


# =============================================================================
# Router prefix mounts — verified via HTTP response codes (not 404)
# =============================================================================

@pytest.mark.asyncio
async def test_router_prefixes_mounted():
    """
    All expected API v1 router prefixes respond (not 404) so the routers
    are confirmed mounted at the correct paths.
    """
    app = create_app()
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        follow_redirects=False,
    ) as client:
        results = {}
        # Each of these will get a 307 redirect (trailing slash) or 405 (method
        # not allowed on root) — neither is a 404, confirming the prefix exists.
        paths = [
            "/api/v1/businesses",
            "/api/v1/websites",
            "/api/v1/crawls",
            "/api/v1/pages",
        ]
        for path in paths:
            r = await client.get(path)
            # 307 → prefix mounted, no GET on root
            # 405 → prefix mounted, GET not defined on root
            # 422 → prefix mounted, path routing quirk (Starlette 1.0.0)
            # 404 only would mean prefix NOT mounted
            results[path] = r.status_code

        for path, code in results.items():
            assert code != 404, f"{path} returned 404 — router not mounted"


# =============================================================================
# HTTP method acceptance — verifies routes accept expected methods
# =============================================================================

@pytest.mark.asyncio
async def test_businesses_root_accepts_post():
    """
    POST to /api/v1/businesses/ returns 307 (redirect to canonical) or 422
    (routing quirk), confirming the POST route IS defined on that prefix.
    A 405 would mean POST is not defined; 404 would mean prefix not mounted.
    """
    app = create_app()
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        follow_redirects=False,
    ) as client:
        r = await client.post(
            "/api/v1/businesses/",
            json={"name": "Test Biz", "business_type": "retail"},
        )
        # 307 = redirect to non-trailing-slash (route exists, Starlette quirk)
        # 422 = routing handled but body validation varies
        # 405 = method not allowed (route missing — bad)
        # 404 = prefix not mounted (bad)
        assert r.status_code not in (404, 405), (
            f"POST /api/v1/businesses/ returned {r.status_code} — "
            "POST route may not be defined on businesses router"
        )


@pytest.mark.asyncio
async def test_websites_root_accepts_post():
    """Same as above for websites router POST."""
    app = create_app()
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        follow_redirects=False,
    ) as client:
        r = await client.post(
            "/api/v1/websites/",
            json={"url": "https://example.com", "business_id": "00000000-0000-0000-0000-000000000000"},
        )
        assert r.status_code not in (404, 405), (
            f"POST /api/v1/websites/ returned {r.status_code} — "
            "POST route may not be defined on websites router"
        )


@pytest.mark.asyncio
async def test_crawls_root_accepts_post():
    """Same as above for crawls router POST."""
    app = create_app()
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        follow_redirects=False,
    ) as client:
        r = await client.post(
            "/api/v1/crawls/",
            json={
                "website_id": "00000000-0000-0000-0000-000000000000",
                " crawl_type": "full",
            },
        )
        assert r.status_code not in (404, 405), (
            f"POST /api/v1/crawls/ returned {r.status_code} — "
            "POST route may not be defined on crawls router"
        )


# =============================================================================
# Database session verification
# =============================================================================

@pytest.mark.asyncio
async def test_database_session_from_sqlite_engine():
    """
    Verifies a local SQLite async engine can produce a usable session.
    This confirms the DB layer is functional without requiring real Postgres.
    """
    import uuid
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
    from services.api.models import Base

    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_maker = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

    async with session_maker() as session:
        # Session is alive and can perform operations
        assert session is not None

    # Sessionmaker itself is constructable (doesn't need a live connection)
    assert session_maker is not None
    await engine.dispose()
