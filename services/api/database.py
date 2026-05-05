# Async database session management.

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from services.api.config import get_settings

settings = get_settings()

# Create async engine — NullPool used when DATABASE_URL is not set (tests)
_connect_args = {"pool_size": settings.db_pool_size, "max_overflow": settings.db_max_overflow}

_async_engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    pool_timeout=settings.db_pool_timeout,
    # Connect args passed to asyncpg
    connect_args={"timeout": 30, "command_timeout": 30},
)

# Session factory
async_session_maker = async_sessionmaker(
    bind=_async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency — yields an async session and ensures it is closed.

    Usage:
        @router.get("/businesses")
        async def list_businesses(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


@asynccontextmanager
async def get_db_context() -> AsyncGenerator[AsyncSession, None]:
    """
    Context manager version of get_db — for use outside FastAPI routes
    (Celery tasks, scripts, etc.).
    """
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
