"""Test that all API routers import cleanly and FastAPI app starts correctly."""
import sys
from pathlib import Path

repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(repo_root))

import pytest


def test_businesses_router_import():
    from services.api.routers import businesses

    assert hasattr(businesses, "router")


def test_websites_router_import():
    from services.api.routers import websites

    assert hasattr(websites, "router")


def test_crawls_router_import():
    from services.api.routers import crawls

    assert hasattr(crawls, "router")


def test_pages_router_import():
    from services.api.routers import pages

    assert hasattr(pages, "router")


def test_seo_issues_router_import():
    from services.api.routers import seo_issues

    assert hasattr(seo_issues, "router")


def test_fastapi_app_imports_with_routers():
    """FastAPI app imports cleanly after all routers are registered."""
    from services.api.main import app

    assert app is not None


def test_health_endpoint_returns_200():
    """Health endpoint returns 200 OK."""
    from starlette.testclient import TestClient

    from services.api.main import app

    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
