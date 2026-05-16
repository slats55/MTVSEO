"""Celery application for SEO Agent OS.

Loads broker configuration from settings.redis_url.
Must be imported after settings are initialized (after database.py).

Usage:
    from services.api.celery_app import celery_app
    from packages.crawler.crawl_worker import crawl_website_task

    # Dispatch
    crawl_website_task.delay(crawl_run_id=..., start_url=..., ...)
"""

from celery import Celery  # type: ignore

from services.api.config import get_settings

_settings = get_settings()

celery_app = Celery(
    "seo_agent_os",
    broker=_settings.redis_url,
    backend=_settings.redis_url,
    include=[
        "packages.crawler.crawl_worker",
    ],
)

# Optional: configure from settings
celery_app.conf.update(
    broker_connection_retry_on_startup=True,
    broker_connection_retry=True,
    broker_connection_max_retries=5,
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)