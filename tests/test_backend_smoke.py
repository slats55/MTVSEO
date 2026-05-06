# Backend smoke tests — verifies the app can be imported and health endpoint responds.
# No DB writes, no external network calls required.

import sys
from pathlib import Path

# Ensure repo root is on path
repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(repo_root))

import pytest


def test_fastapi_app_imports():
    """FastAPI app and all routers/models import without errors."""
    from services.api.main import app

    assert app is not None
    assert app.title == "SEO Agent OS API"


def test_health_endpoint():
    """Health endpoint returns healthy status."""
    from fastapi.testclient import TestClient

    from services.api.main import app

    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data.get("status") == "healthy"


def test_packages_import():
    """All core packages import without errors."""
    import packages.crawler
    import packages.content_engine
    import packages.geo_audit
    import packages.schema_engine
    import packages.seo_audit
    import packages.shared

    # smoke-check key exports exist
    from packages.seo_audit import AuditScore
    from packages.geo_audit.models import GeoScore
    from packages.content_engine import BriefGenerator
    from packages.schema_engine import SchemaValidator
    from packages.shared import get_logger

    assert AuditScore is not None
    assert GeoScore is not None
    assert BriefGenerator is not None
    assert SchemaValidator is not None
    assert callable(get_logger)


def test_database_config_sanity():
    """DB config loads without crashing (uses .env or fallback)."""
    from services.api.config import settings

    # settings should have a DATABASE_URL or fallback
    assert settings is not None
    # SQLite fallback is acceptable for local dev
    db_url = str(settings.database_url)
    assert db_url.startswith("sqlite://") or db_url.startswith("postgresql+")


if __name__ == "__main__":
    pytest.main([__file__, "-q"])
