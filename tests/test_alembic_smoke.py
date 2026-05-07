"""Test Alembic migration visibility — no full migration run required."""
import subprocess
import sys
from pathlib import Path

repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(repo_root))


def test_alembic_heads_discovers_migration():
    """Alembic can discover the migration head without running it."""
    result = subprocess.run(
        [
            sys.executable, "-m", "alembic",
            "-c", "services/api/alembic.ini",
            "heads"
        ],
        cwd=str(repo_root),
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, f"alembic heads failed: {result.stderr}"
    # Expected: 20260505_1200 (head)
    assert "20260505_1200" in result.stdout, f"Expected migration head not found in: {result.stdout}"


def test_alembic_shows_migration_info():
    """Alembic can show details of the current migration."""
    result = subprocess.run(
        [
            sys.executable, "-m", "alembic",
            "-c", "services/api/alembic.ini",
            "show", "20260505_1200"
        ],
        cwd=str(repo_root),
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, f"alembic show failed: {result.stderr}"


def test_initial_migration_file_exists():
    """The initial migration file is present on disk."""
    migrations_dir = repo_root / "services" / "api" / "migrations" / "versions"
    migration_file = migrations_dir / "20260505_1200_initial_migration.py"
    assert migration_file.exists(), f"Migration file not found: {migration_file}"
