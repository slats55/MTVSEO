#!/usr/bin/env python3
"""
Local environment verification script for seo-agent-os.

Run from repo root:
    python scripts/verify_local.py

No external network required. No destructive DB writes.
Exits 0 on full pass, non-zero on any failure.
"""

import sys
from pathlib import Path

repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(repo_root))

PASS = "\033[92m✓\033[0m"
FAIL = "\033[91m✗\033[0m"


def check(label: str, fn) -> bool:
    try:
        result = fn()
        if result is not None and not result:
            print(f"  {FAIL} {label}")
            return False
        print(f"  {PASS} {label}")
        return True
    except Exception as ex:
        print(f"  {FAIL} {label}: {ex}")
        return False


def main() -> int:
    print("=" * 60)
    print("SEO Agent OS — Local Environment Verification")
    print("=" * 60)

    all_pass = True

    # 1. Python version
    print("\n[1] Python version")
    major, minor = sys.version_info[:2]
    all_pass &= check(f"Python {major}.{minor} >= 3.11", lambda: major == 3 and minor >= 11)

    # 2. Required standard-library and third-party imports
    print("\n[2] Required dependency imports")
    deps = [
        ("fastapi", "fastapi"),
        ("uvicorn", "uvicorn"),
        ("sqlalchemy", "sqlalchemy"),
        ("pydantic", "pydantic"),
        ("httpx", "httpx"),
        ("beautifulsoup4", "bs4"),
        ("lxml", "lxml"),
        ("requests", "requests"),
        ("celery", "celery"),
        ("redis", "redis"),
        ("alembic", "alembic"),
        ("pytest", "pytest"),
        ("ruff", "ruff"),
    ]
    for label, import_name in deps:
        all_pass &= check(f"{label}", lambda il=import_name: __import__(il))

    # 3. Package imports
    print("\n[3] Package imports (no network)")
    packages_ok = True
    try:
        import packages.crawler
        import packages.content_engine
        import packages.geo_audit
        import packages.schema_engine
        import packages.seo_audit
        import packages.shared
        import packages.reporting
        import packages.integrations
    except Exception as ex:
        print(f"  {FAIL} package imports: {ex}")
        packages_ok = False
    if packages_ok:
        print(f"  {PASS} all packages importable")
    all_pass &= packages_ok

    # 4. Key package exports
    print("\n[4] Package exports sanity-check")
    export_checks = [
        ("packages.seo_audit", "AuditScore"),
        ("packages.geo_audit.models", "GeoScore"),
        ("packages.content_engine", "BriefGenerator"),
        ("packages.schema_engine", "SchemaValidator"),
        ("packages.shared", "get_logger"),
        ("packages.shared", "SeoAgentException"),
        ("packages.crawler", "CrawlRunner"),
        ("packages.reporting", "AuditReportGenerator"),
    ]
    for module_name, export_name in export_checks:
        try:
            mod = __import__(module_name, fromlist=[export_name])
            assert getattr(mod, export_name, None) is not None
            print(f"  {PASS} {module_name}.{export_name}")
        except Exception as ex:
            print(f"  {FAIL} {module_name}.{export_name}: {ex}")
            all_pass = False

    # 5. FastAPI app import
    print("\n[5] FastAPI app import")
    all_pass &= check("services.api.main imports", lambda: (
        __import__("services.api.main"),
        True
    )[1])

    # 6. Health endpoint via TestClient
    print("\n[6] Health endpoint (TestClient, no network)")
    try:
        from fastapi.testclient import TestClient
        from services.api.main import app
        client = TestClient(app)
        response = client.get("/health")
        if response.status_code == 200 and response.json().get("status") == "healthy":
            print(f"  {PASS} /health returns 200 healthy")
        else:
            print(f"  {FAIL} /health status={response.status_code}")
            all_pass = False
    except Exception as ex:
        print(f"  {FAIL} /health: {ex}")
        all_pass = False

    # 7. DB config sanity
    print("\n[7] DB config sanity (SQLite fallback acceptable)")
    try:
        from services.api.config import settings
        db_url = str(settings.database_url)
        ok = db_url.startswith("sqlite://") or db_url.startswith("postgresql+")
        if ok:
            print(f"  {PASS} DATABASE_URL configured ({db_url.split('://')[0]})")
        else:
            print(f"  {FAIL} Unexpected DATABASE_URL scheme: {db_url}")
            all_pass = False
    except Exception as ex:
        print(f"  {FAIL} settings import: {ex}")
        all_pass = False

    # Summary
    print("\n" + "=" * 60)
    if all_pass:
        print(f"{PASS} ALL CHECKS PASSED — repo is ready for Codex")
        print("=" * 60)
        return 0
    else:
        print(f"{FAIL} SOME CHECKS FAILED — fix before continuing")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
