# DB-backed CRUD endpoint tests — real async SQLite session, httpx.AsyncClient.
#
# Test approach:
# - Fresh in-memory SQLite per test (isolated, no cross-test pollution)
# - All Base tables created via metadata.create_all
# - Placeholder user seeded with real UUID object (required by Business.user FK)
# - FastAPI dependency_overrides[get_db] = test async sessionmaker
# - httpx.AsyncClient + ASGITransport calls real async router handlers
#
# Routing: Each resource has a distinct path prefix:
#   /api/v1/businesses/   — businesses
#   /api/v1/websites/     — websites
#   /api/v1/crawls/       — crawl runs
#
# No Postgres, Redis, Celery, or external APIs required.

import uuid

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from sqlalchemy.pool import StaticPool
from services.api.database import get_db
from services.api.models import Base, User
from services.api.models.business import Business
from services.api.models.crawl_run import CrawlRun
from services.api.models.website import Website
from services.api.models.page import Page
from services.api.models.seo_issue import SeoIssue
from services.api.models.enums import IssueSeverity, CrawlStatus
from services.api.main import create_app

# Placeholder user ID — matches hardcoded user_id in businesses.py::create_business
_PLACEHOLDER_USER_ID = uuid.UUID("00000000-0000-0000-0000-000000000000")


class ClientFixture:
    """
    Bundles the async HTTP client with the test session_maker
    so tests can verify DB state after making API calls.
    """

    def __init__(self, app, ac: AsyncClient, session_maker):
        self.app = app
        self.ac = ac
        self._session_maker = session_maker

    async def verify_business_in_db(self, biz_uuid: uuid.UUID) -> dict | None:
        """Verify business exists in DB via raw SQL. Returns dict with record data or None."""
        async with self._session_maker() as session:
            result = await session.execute(
                text("SELECT id, name, user_id, business_type, location FROM businesses WHERE id=:id"),
                {"id": biz_uuid.hex},
            )
            row = result.fetchone()
            if row is None:
                return None
            return {"id": str(row[0]), "name": row[1], "user_id": str(row[2]),
                    "business_type": row[3], "location": row[4]}

    async def verify_website_in_db(self, site_uuid: uuid.UUID) -> dict | None:
        """Verify website exists in DB via raw SQL. Returns dict with record data or None."""
        async with self._session_maker() as session:
            result = await session.execute(
                text("SELECT id, url, business_id FROM websites WHERE id=:id"),
                {"id": site_uuid.hex},
            )
            row = result.fetchone()
            if row is None:
                return None
            return {"id": str(row[0]), "url": row[1], "business_id": str(row[2])}

    async def verify_crawl_in_db(self, crawl_uuid: uuid.UUID) -> dict | None:
        """Verify crawl exists in DB via raw SQL. Returns dict with record data or None."""
        async with self._session_maker() as session:
            result = await session.execute(
                text("SELECT id, website_id, status, crawl_depth FROM crawl_runs WHERE id=:id"),
                {"id": crawl_uuid.hex},
            )
            row = result.fetchone()
            if row is None:
                return None
            return {"id": str(row[0]), "website_id": str(row[1]),
                    "status": row[2], "crawl_depth": row[3]}


@pytest_asyncio.fixture
async def async_client():
    """
    Per-test async SQLite test database with all tables created,
    a placeholder user seeded, and a wired AsyncClient.

    Yields a ClientFixture containing (app, AsyncClient).
    """
    engine = create_async_engine(
        "sqlite+aiosqlite:///file::memory:?cache=shared&uri=true",
        echo=False,
        connect_args={"check_same_thread": False, "uri": True},
    )
    session_maker = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Seed placeholder user (required by create_business which hardcodes user_id)
    async with session_maker() as session:
        user = User(
            id=_PLACEHOLDER_USER_ID,
            email="test@test.com",
            name="Test User",
            password_hash="dummy_hash_for_testing_only",
        )
        session.add(user)
        await session.commit()

    async def override_get_db():
        async with session_maker() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    app = create_app()
    # redirect_slashes=False prevents trailing-slash redirects that would turn POST into GET
    app.router.redirect_slashes = False
    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        follow_redirects=False,
    ) as ac:
        yield ClientFixture(app, ac, session_maker)

    app.dependency_overrides.clear()
    await engine.dispose()


# =============================================================================
# POST /api/v1/businesses/ — create
# GET /api/v1/businesses/  — list
# GET /api/v1/businesses/{id} — read single
# =============================================================================

@pytest.mark.asyncio
async def test_create_business(async_client: ClientFixture):
    """POST /api/v1/businesses/ creates a business and returns 201 with the record."""
    resp = await async_client.ac.post("/api/v1/businesses/", json={
        "name": "Acme Dispensary",
        "business_type": "retail",
        "location": "Denver, CO",
        "is_cannabis": True,
    })

    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data["name"] == "Acme Dispensary"
    assert data["business_type"] == "retail"
    assert data["location"] == "Denver, CO"
    assert data["is_cannabis"] is True
    assert "id" in data
    biz_uuid = uuid.UUID(data["id"])

    # Verify DB record
    biz = await async_client.verify_business_in_db(biz_uuid)
    assert biz is not None
    assert biz["name"] == "Acme Dispensary"
    assert biz["business_type"] == "retail"
    assert str(biz["user_id"]).replace("-", "") == str(_PLACEHOLDER_USER_ID).replace("-", "")


@pytest.mark.asyncio
async def test_create_business_minimal(async_client: ClientFixture):
    """POST /api/v1/businesses/ with only the required field 'name' returns 201."""
    resp = await async_client.ac.post("/api/v1/businesses/", json={"name": "Minimal Biz"})

    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Minimal Biz"
    assert "id" in data


@pytest.mark.asyncio
async def test_create_business_missing_name_returns_422(async_client: ClientFixture):
    """POST /api/v1/businesses/ without 'name' returns 422 validation error."""
    resp = await async_client.ac.post("/api/v1/businesses/", json={})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_list_businesses(async_client: ClientFixture):
    """GET /api/v1/businesses/ returns a paginated list of businesses."""
    for name in ["List Biz Alpha", "List Biz Beta"]:
        await async_client.ac.post("/api/v1/businesses/", json={"name": name})

    resp = await async_client.ac.get("/api/v1/businesses/")
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data
    assert "total" in data
    assert data["total"] >= 2
    names = {item["name"] for item in data["items"]}
    assert "List Biz Alpha" in names
    assert "List Biz Beta" in names


@pytest.mark.asyncio
async def test_get_business_by_id(async_client: ClientFixture):
    """GET /api/v1/businesses/{id} returns the correct business record."""
    # Create
    create_resp = await async_client.ac.post("/api/v1/businesses/", json={"name": "Fetch Test Biz"})
    assert create_resp.status_code == 201
    biz_id = create_resp.json()["id"]

    # Read
    get_resp = await async_client.ac.get(f"/api/v1/businesses/{biz_id}")
    assert get_resp.status_code == 200
    data = get_resp.json()
    assert data["id"] == biz_id
    assert data["name"] == "Fetch Test Biz"


@pytest.mark.asyncio
async def test_get_business_not_found(async_client: ClientFixture):
    """GET /api/v1/businesses/{nonexistent_id} returns 404."""
    fake_id = str(uuid.uuid4())
    resp = await async_client.ac.get(f"/api/v1/businesses/{fake_id}")
    assert resp.status_code == 404


# =============================================================================
# POST /api/v1/websites/ — create
# GET /api/v1/websites/  — list
# GET /api/v1/websites/{id} — read single
# =============================================================================

@pytest.mark.asyncio
async def test_create_website(async_client: ClientFixture):
    """POST /api/v1/websites/ creates a website linked to a business."""
    # Create parent business first
    biz_resp = await async_client.ac.post("/api/v1/businesses/", json={"name": "Biz For Website Test"})
    assert biz_resp.status_code == 201
    biz_id = biz_resp.json()["id"]

    # Create website
    site_resp = await async_client.ac.post("/api/v1/websites/", json={
        "business_id": biz_id,
        "url": "https://acme-dispensary.example.com",
        "name": "Acme Website",
    })

    assert site_resp.status_code == 201, f"Expected 201, got {site_resp.status_code}: {site_resp.text}"
    site_data = site_resp.json()
    assert site_data["business_id"] == biz_id
    assert site_data["url"] == "https://acme-dispensary.example.com"

    # Verify DB
    site_uuid = uuid.UUID(site_data["id"])
    site = await async_client.verify_website_in_db(site_uuid)
    assert site is not None
    assert str(site["business_id"]).replace("-", "") == str(uuid.UUID(biz_id)).replace("-", "")


@pytest.mark.asyncio
async def test_create_website_requires_valid_business(async_client: ClientFixture):
    """POST /api/v1/websites/ with nonexistent business_id returns 404."""
    fake_biz_id = str(uuid.uuid4())
    resp = await async_client.ac.post("/api/v1/websites/", json={
        "business_id": fake_biz_id,
        "url": "https://example.com",
    })
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_get_website_by_id(async_client: ClientFixture):
    """GET /api/v1/websites/{id} returns the correct website."""
    biz_resp = await async_client.ac.post("/api/v1/businesses/", json={"name": "Site GET Test"})
    biz_id = biz_resp.json()["id"]
    site_resp = await async_client.ac.post("/api/v1/websites/", json={
        "business_id": biz_id,
        "url": "https://get-site.example.com",
    })
    site_id = site_resp.json()["id"]

    get_resp = await async_client.ac.get(f"/api/v1/websites/{site_id}")
    assert get_resp.status_code == 200
    data = get_resp.json()
    assert data["id"] == site_id
    assert data["url"] == "https://get-site.example.com"


# =============================================================================
# POST /api/v1/crawls/ — create
# GET /api/v1/crawls/  — list
# GET /api/v1/crawls/{id} — read single
# =============================================================================

@pytest.mark.asyncio
async def test_create_crawl(async_client: ClientFixture):
    """POST /api/v1/crawls/ creates a CrawlRun with PENDING status."""
    # Setup: business → website
    biz_resp = await async_client.ac.post("/api/v1/businesses/", json={"name": "Biz For Crawl Test"})
    assert biz_resp.status_code == 201
    biz_id = biz_resp.json()["id"]

    site_resp = await async_client.ac.post("/api/v1/websites/", json={
        "business_id": biz_id,
        "url": "https://crawl-target.example.com",
    })
    assert site_resp.status_code == 201
    site_id = site_resp.json()["id"]

    # Create crawl run
    crawl_resp = await async_client.ac.post("/api/v1/crawls/", json={
        "website_id": site_id,
        "crawl_depth": 2,
        "max_pages": 10,
    })

    assert crawl_resp.status_code == 201, f"Expected 201, got {crawl_resp.status_code}: {crawl_resp.text}"
    crawl_data = crawl_resp.json()
    assert crawl_data["website_id"] == site_id
    assert crawl_data["status"] == "PENDING"
    assert crawl_data["crawl_depth"] == 2
    assert crawl_data["max_pages"] == 10

    # Verify DB
    crawl_uuid = uuid.UUID(crawl_data["id"])
    crawl = await async_client.verify_crawl_in_db(crawl_uuid)
    assert crawl is not None
    assert str(crawl["website_id"]).replace("-", "") == str(uuid.UUID(site_id)).replace("-", "")


@pytest.mark.asyncio
async def test_create_crawl_requires_valid_website(async_client: ClientFixture):
    """POST /api/v1/crawls/ with nonexistent website_id returns 404."""
    fake_site_id = str(uuid.uuid4())
    resp = await async_client.ac.post("/api/v1/crawls/", json={"website_id": fake_site_id})
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_get_crawl_by_id(async_client: ClientFixture):
    """GET /api/v1/crawls/{id} returns the correct crawl run."""
    # Setup
    biz_resp = await async_client.ac.post("/api/v1/businesses/", json={"name": "Crawl GET Test"})
    biz_id = biz_resp.json()["id"]
    site_resp = await async_client.ac.post("/api/v1/websites/", json={
        "business_id": biz_id,
        "url": "https://get-crawl.example.com",
    })
    site_id = site_resp.json()["id"]
    crawl_resp = await async_client.ac.post("/api/v1/crawls/", json={"website_id": site_id})
    crawl_id = crawl_resp.json()["id"]

    # Read
    get_resp = await async_client.ac.get(f"/api/v1/crawls/{crawl_id}")
    assert get_resp.status_code == 200
    data = get_resp.json()
    assert data["id"] == crawl_id
    assert data["status"] == "PENDING"


# =============================================================================
# GET /api/v1/seo-issues/  — list (no POST endpoint; SeoIssues created by crawls)
# GET /api/v1/seo-issues/{id} — read single
# =============================================================================

@pytest.mark.asyncio
async def test_list_seo_issues_empty(async_client: ClientFixture):
    """GET /api/v1/seo-issues/ with no records returns 200 with empty items list."""
    resp = await async_client.ac.get("/api/v1/seo-issues/")
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert "items" in data
    assert "total" in data
    assert data["items"] == []
    assert data["total"] == 0


@pytest.mark.asyncio
async def test_list_seo_issues_returns_seeded_records(async_client: ClientFixture):
    """GET /api/v1/seo-issues/ returns seeded SeoIssue records."""
    # Setup: business → website → crawl_run → page → seo_issue
    biz_resp = await async_client.ac.post("/api/v1/businesses/", json={"name": "Biz For SeoIssue Test"})
    assert biz_resp.status_code == 201
    biz_id = biz_resp.json()["id"]

    site_resp = await async_client.ac.post("/api/v1/websites/", json={
        "business_id": biz_id,
        "url": "https://seo-issue-test.example.com",
    })
    assert site_resp.status_code == 201
    site_id = site_resp.json()["id"]

    crawl_resp = await async_client.ac.post("/api/v1/crawls/", json={"website_id": site_id})
    assert crawl_resp.status_code == 201
    crawl_id = crawl_resp.json()["id"]

    # Create Page and SeoIssue directly in DB (no POST endpoints for these)
    page_uuid = uuid.uuid4()
    seo_issue_uuid = uuid.uuid4()

    async with async_client._session_maker() as session:
        page = Page(
            id=page_uuid,
            crawl_run_id=uuid.UUID(crawl_id),
            url="https://seo-issue-test.example.com/page1",
            title="Test Page",
            status_code=200,
        )
        session.add(page)
        await session.flush()

        seo_issue = SeoIssue(
            id=seo_issue_uuid,
            page_id=page_uuid,
            crawl_run_id=uuid.UUID(crawl_id),
            issue_type="missing_h1",
            severity=IssueSeverity.HIGH,
            title="H1 tag is missing",
            description="The page does not have an H1 tag.",
            recommendation="Add an H1 tag to the page.",
            affected_element="/html/head/h1",
        )
        session.add(seo_issue)
        await session.commit()

    # List endpoint
    resp = await async_client.ac.get("/api/v1/seo-issues/")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 1
    items_by_id = {item["id"]: item for item in data["items"]}
    assert str(seo_issue_uuid) in items_by_id
    item = items_by_id[str(seo_issue_uuid)]
    assert item["issue_type"] == "missing_h1"
    assert item["severity"] == "HIGH"
    assert item["title"] == "H1 tag is missing"


@pytest.mark.asyncio
async def test_list_seo_issues_filtered_by_crawl_run(async_client: ClientFixture):
    """GET /api/v1/seo-issues/?crawl_run_id= filters correctly."""
    # Setup same chain and create two SeoIssues
    biz_resp = await async_client.ac.post("/api/v1/businesses/", json={"name": "Biz For Filter Test"})
    biz_id = biz_resp.json()["id"]
    site_resp = await async_client.ac.post("/api/v1/websites/", json={
        "business_id": biz_id,
        "url": "https://filter-test.example.com",
    })
    site_id = site_resp.json()["id"]
    crawl_resp = await async_client.ac.post("/api/v1/crawls/", json={"website_id": site_id})
    crawl_id = crawl_resp.json()["id"]

    page_uuid = uuid.uuid4()
    seo_issue_uuid = uuid.uuid4()

    async with async_client._session_maker() as session:
        page = Page(
            id=page_uuid,
            crawl_run_id=uuid.UUID(crawl_id),
            url="https://filter-test.example.com/page1",
            title="Filter Test Page",
            status_code=200,
        )
        session.add(page)
        await session.flush()

        seo_issue = SeoIssue(
            id=seo_issue_uuid,
            page_id=page_uuid,
            crawl_run_id=uuid.UUID(crawl_id),
            issue_type="missing_meta_description",
            severity=IssueSeverity.MEDIUM,
            title="Meta description missing",
            description="The page is missing a meta description.",
        )
        session.add(seo_issue)
        await session.commit()

    # Filter by crawl_run_id
    resp = await async_client.ac.get(f"/api/v1/seo-issues/?crawl_run_id={crawl_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 1
    assert all(item["crawl_run_id"] == crawl_id for item in data["items"])

    # Filter by unrelated ID returns empty
    fake_id = str(uuid.uuid4())
    resp2 = await async_client.ac.get(f"/api/v1/seo-issues/?crawl_run_id={fake_id}")
    assert resp2.status_code == 200
    assert resp2.json()["items"] == []


@pytest.mark.asyncio
async def test_get_seo_issue_by_id(async_client: ClientFixture):
    """GET /api/v1/seo-issues/{id} returns the correct SEO issue record."""
    # Setup chain
    biz_resp = await async_client.ac.post("/api/v1/businesses/", json={"name": "Biz For Get SeoIssue"})
    biz_id = biz_resp.json()["id"]
    site_resp = await async_client.ac.post("/api/v1/websites/", json={
        "business_id": biz_id,
        "url": "https://get-seo-issue.example.com",
    })
    site_id = site_resp.json()["id"]
    crawl_resp = await async_client.ac.post("/api/v1/crawls/", json={"website_id": site_id})
    crawl_id = crawl_resp.json()["id"]

    page_uuid = uuid.uuid4()
    seo_issue_uuid = uuid.uuid4()

    async with async_client._session_maker() as session:
        page = Page(
            id=page_uuid,
            crawl_run_id=uuid.UUID(crawl_id),
            url="https://get-seo-issue.example.com/page1",
            status_code=200,
        )
        session.add(page)
        await session.flush()

        seo_issue = SeoIssue(
            id=seo_issue_uuid,
            page_id=page_uuid,
            crawl_run_id=uuid.UUID(crawl_id),
            issue_type="duplicate_title",
            severity=IssueSeverity.INFO,
            title="Duplicate title tag",
            description="Title tag appears more than once.",
            recommendation="Use unique title tags for each page.",
            affected_element="/html/head/title",
        )
        session.add(seo_issue)
        await session.commit()

    # Read by ID
    get_resp = await async_client.ac.get(f"/api/v1/seo-issues/{seo_issue_uuid}")
    assert get_resp.status_code == 200
    data = get_resp.json()
    assert data["id"] == str(seo_issue_uuid)
    assert data["issue_type"] == "duplicate_title"
    assert data["severity"] == "INFO"
    assert data["title"] == "Duplicate title tag"


@pytest.mark.asyncio
async def test_get_seo_issue_not_found(async_client: ClientFixture):
    """GET /api/v1/seo-issues/{nonexistent_id} returns 404."""
    fake_id = str(uuid.uuid4())
    resp = await async_client.ac.get(f"/api/v1/seo-issues/{fake_id}")
    assert resp.status_code == 404
