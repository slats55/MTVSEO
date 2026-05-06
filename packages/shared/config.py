# Shared configuration constants and helpers.
# No internal dependencies.

import os
from datetime import timedelta


# ─── Application ──────────────────────────────────────────────────────────────


APP_NAME = "SEO Agent OS"
APP_ENV = os.environ.get("APP_ENV", "development")
IS_PRODUCTION = APP_ENV == "production"
IS_DEVELOPMENT = APP_ENV == "development"


# ─── API ──────────────────────────────────────────────────────────────────────


API_V1_PREFIX = "/api/v1"
API_TITLE = "SEO Agent OS API"
API_VERSION = "1.0.0"
API_DESCRIPTION = "Autonomous SEO and GEO agent system API"


# ─── Database ─────────────────────────────────────────────────────────────────


DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/seo_agent_os"
)
SYNC_DATABASE_URL = os.environ.get(
    "SYNC_DATABASE_URL",
    "postgresql://postgres:***@localhost:5432/seo_agent_os"
)

# Connection pool settings
DB_POOL_SIZE = int(os.environ.get("DB_POOL_SIZE", "10"))
DB_MAX_OVERFLOW = int(os.environ.get("DB_MAX_OVERFLOW", "20"))
DB_POOL_TIMEOUT = int(os.environ.get("DB_POOL_TIMEOUT", "30"))


# ─── Redis ────────────────────────────────────────────────────────────────────


REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")


# ─── AI / Hermes ──────────────────────────────────────────────────────────────


HERMES_API_KEY = os.environ.get("HERMES_API_KEY", "")
HERMES_ENDPOINT = os.environ.get("HERMES_ENDPOINT", "http://localhost:8080")
HERMES_TIMEOUT = int(os.environ.get("HERMES_TIMEOUT", "120"))

# Model routing
AI_MODEL_EXTRACTION = "miniimax-text-001"   # Cheap, fast — crawling, parsing
AI_MODEL_STRATEGY   = "miniimax-text-002"    # Strong — recommendations, scoring
AI_MODEL_CONTENT    = "miniimax-text-002"    # Strong — content generation
AI_MODEL_EDITOR     = "miniimax-text-002"    # Strong — editorial review


# ─── Crawler defaults ────────────────────────────────────────────────────────


DEFAULT_MAX_PAGES = int(os.environ.get("DEFAULT_MAX_PAGES", "50"))
DEFAULT_CRAWL_DEPTH = int(os.environ.get("DEFAULT_CRAWL_DEPTH", "3"))
DEFAULT_CRAWL_DELAY_MS = int(os.environ.get("DEFAULT_CRAWL_DELAY_MS", "500"))
DEFAULT_CRAWL_TIMEOUT_MS = int(os.environ.get("DEFAULT_CRAWL_TIMEOUT_MS", "15000"))
DEFAULT_USER_AGENT = os.environ.get(
    "DEFAULT_USER_AGENT",
    "SEO-Agent-OS/1.0 (+https://github.com/seo-agent-os)"
)


# ─── Storage ──────────────────────────────────────────────────────────────────


STORAGE_BACKEND = os.environ.get("STORAGE_BACKEND", "local")  # "local" or "s3"
STORAGE_PATH = os.environ.get("STORAGE_PATH", "./storage")

REPORTS_DIR = os.path.join(STORAGE_PATH, "reports")
EXPORTS_DIR = os.path.join(STORAGE_PATH, "exports")
SNAPSHOTS_DIR = os.path.join(STORAGE_PATH, "crawl-snapshots")
SCHEMA_OUTPUTS_DIR = os.path.join(STORAGE_PATH, "schema-outputs")


# ─── Security ─────────────────────────────────────────────────────────────────


SECRET_KEY = os.environ.get("SECRET_KEY", "change-me-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))


# ─── External APIs ─────────────────────────────────────────────────────────────


GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "")
GOOGLE_SEARCH_CONSOLE_CLIENT_ID = os.environ.get("GOOGLE_SEARCH_CONSOLE_CLIENT_ID", "")
GOOGLE_SEARCH_CONSOLE_CLIENT_SECRET = os.environ.get("GOOGLE_SEARCH_CONSOLE_CLIENT_SECRET", "")


# ─── Rate limiting ────────────────────────────────────────────────────────────


RATE_LIMIT_PER_MINUTE = int(os.environ.get("RATE_LIMIT_PER_MINUTE", "60"))
CRAWL_DELAY_SECONDS = float(os.environ.get("CRAWL_DELAY_SECONDS", "0.5"))


# ─── Celery ───────────────────────────────────────────────────────────────────


CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL


# ─── Logging ───────────────────────────────────────────────────────────────────


LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s | %(name)s | %(levelname)s | %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
