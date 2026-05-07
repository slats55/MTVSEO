#!/usr/bin/env bash
# run_dev.sh — Start the SEO Agent OS API in development mode.
# Requirements: Python 3.12+, .venv set up in project root.
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
VENV_PYTHON="$PROJECT_ROOT/.venv/bin/python3"
APP_MODULE="services.api.main:app"

cd "$PROJECT_ROOT"

# ── Python path ──────────────────────────────────────────────────────────────
export PYTHONPATH="$PROJECT_ROOT"

# ── Python executable ─────────────────────────────────────────────────────────
if [[ ! -x "$VENV_PYTHON" ]]; then
    echo "ERROR: Python venv not found at $VENV_PYTHON"
    echo "Run: python3 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt"
    exit 1
fi

# ── Verify app imports ───────────────────────────────────────────────────────
echo "[run_dev] Verifying app imports..."
"$VENV_PYTHON" -c "from services.api.main import app; print(f'  App title: {app.title}')" 2>/dev/null || {
    echo "ERROR: Cannot import services.api.main. Check PYTHONPATH and dependencies."
    exit 1
}

# ── .env check ────────────────────────────────────────────────────────────────
if [[ ! -f "$PROJECT_ROOT/.env" ]]; then
    echo "WARNING: .env not found at $PROJECT_ROOT/.env"
    echo "  Using defaults from services/api/config.py"
    echo "  Copy .env.example to .env and configure for production use."
fi

# ── Database mode (no secrets exposed) ──────────────────────────────────────
DATABASE_URL="${DATABASE_URL:-}"
if [[ -n "$DATABASE_URL" ]]; then
    # Show driver type only, not credentials
    DRIVER="$(echo "$DATABASE_URL" | sed 's|://.*@|://***@|' | sed 's|:.*/|\n|' | head -1 || echo "unknown")"
    echo "[run_dev] Database: $DRIVER"
else
    echo "[run_dev] Database: default (postgresql+asyncpg)"
fi

# ── Redis check (optional) ────────────────────────────────────────────────────
REDIS_URL="${REDIS_URL:-}"
if [[ -z "$REDIS_URL" ]]; then
    echo "[run_dev] Redis: not configured — Celery tasks will be disabled"
else
    echo "[run_dev] Redis: configured"
fi

# ── Start uvicorn ────────────────────────────────────────────────────────────
echo ""
echo "[run_dev] Starting FastAPI dev server..."
echo "[run_dev] API docs: http://localhost:8000/docs"
echo "[run_dev] Press Ctrl+C to stop"
echo ""
exec "$VENV_PYTHON" -m uvicorn "$APP_MODULE" \
    --host 0.0.0.0 \
    --port 8000 \
    --reload
