# Shared logging configuration.
# Import from any package to get consistent, structured logging.

import logging
import sys

from packages.shared.config import (
    APP_NAME,
    LOG_DATE_FORMAT,
    LOG_FORMAT,
    LOG_LEVEL,
)


def get_logger(name: str) -> logging.Logger:
    """
    Return a configured logger for the given name.

    Usage:
        from packages.shared.logging import get_logger
        logger = get_logger(__name__)
        logger.info("Starting crawl", extra={"website_id": str(website_id)})
    """
    logger = logging.getLogger(name)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(getattr(logging, LOG_LEVEL.upper(), logging.INFO))

        formatter = logging.Formatter(fmt=LOG_FORMAT, datefmt=LOG_DATE_FORMAT)
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    logger.setLevel(getattr(logging, LOG_LEVEL.upper(), logging.INFO))
    logger.propagate = False

    return logger


def configure_root_logger() -> None:
    """
    Configure the root logger for the entire application.
    Call once at application startup.
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, LOG_LEVEL.upper(), logging.INFO))

    if not root_logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(fmt=LOG_FORMAT, datefmt=LOG_DATE_FORMAT))
        root_logger.addHandler(handler)


# ─── Structured log helpers ───────────────────────────────────────────────────


def log_audit_event(
    logger: logging.Logger,
    level: str,
    message: str,
    *,
    business_id: str | None = None,
    website_id: str | None = None,
    crawl_run_id: str | None = None,
    **extra,
) -> None:
    """Log an structured audit event with consistent fields."""
    ctx = {
        "business_id": str(business_id) if business_id else None,
        "website_id": str(website_id) if website_id else None,
        "crawl_run_id": str(crawl_run_id) if crawl_run_id else None,
        **extra,
    }
    ctx = {k: v for k, v in ctx.items() if v is not None}
    getattr(logger, level.lower())(message, extra=ctx)


def log_crawl_event(
    logger: logging.Logger,
    level: str,
    message: str,
    *,
    crawl_run_id: str | None = None,
    url: str | None = None,
    status_code: int | None = None,
    **extra,
) -> None:
    """Log a structured crawl event."""
    ctx = {
        "crawl_run_id": str(crawl_run_id) if crawl_run_id else None,
        "url": url,
        "status_code": status_code,
        **extra,
    }
    ctx = {k: v for k, v in ctx.items() if v is not None}
    getattr(logger, level.lower())(message, extra=ctx)
