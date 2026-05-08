# FastAPI application entry point.

from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from packages.shared import configure_root_logger, get_logger
from packages.shared.exceptions import SeoAgentException
from services.api.config import get_settings
from services.api.routers import businesses, crawls, pages, websites

settings = get_settings()
logger = get_logger(__name__)


# ─── Lifespan ──────────────────────────────────────────────────────────────────


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan — startup and shutdown events.
    Configure root logger on startup.
    """
    configure_root_logger()
    logger.info(
        "SEO Agent OS starting",
        extra={
            "app_env": settings.app_env,
            "debug": settings.debug,
        },
    )
    yield
    logger.info("SEO Agent OS shutting down")


# ─── App factory ───────────────────────────────────────────────────────────────


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.api_title,
        description=settings.api_description,
        version=settings.api_version,
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # ── CORS ──────────────────────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Exception handlers ────────────────────────────────────────────────────

    @app.exception_handler(SeoAgentException)
    async def seo_agent_exception_handler(
        request: Request, exc: SeoAgentException
    ) -> JSONResponse:
        """Handle all SEO Agent OS exceptions as RFC 7807 Problem Details."""
        return JSONResponse(
            status_code=400,
            content={
                "type": f"https://seo-agent-os.dev/errors/{exc.__class__.__name__.lower()}",
                "title": exc.message,
                "detail": exc.detail,
                "status": 400,
            },
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        """Catch-all — return 500 without leaking internal details."""
        logger.error("Unhandled exception", extra={"error": str(exc), "path": request.url.path})
        return JSONResponse(
            status_code=500,
            content={
                "type": "https://seo-agent-os.dev/errors/internal-error",
                "title": "Internal server error",
                "status": 500,
            },
        )

    # ── Health check ─────────────────────────────────────────────────────────
    @app.get("/health", tags=["health"])
    async def health_check() -> dict:
        return {
            "status": "healthy",
            "app": "seo-agent-os",
            "version": settings.api_version,
            "env": settings.app_env,
        }

    # ── Include routers ──────────────────────────────────────────────────────
    api_prefix = settings.api_v1_prefix
    app.include_router(businesses.router, prefix=api_prefix, tags=["businesses"])
    app.include_router(websites.router, prefix=api_prefix, tags=["websites"])
    app.include_router(crawls.router, prefix=api_prefix, tags=["crawls"])
    app.include_router(pages.router, prefix=api_prefix, tags=["pages"])

    # Disable trailing-slash redirects globally — tests use specific paths
    # and FastAPI's default redirect_slashes=True issues 307s that convert
    # POST to GET when a route both with and without trailing slash exists.
    app.router.redirect_slashes = False

    return app


app = create_app()
