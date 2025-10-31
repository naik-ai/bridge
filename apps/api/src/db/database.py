"""
Database connection management with async SQLAlchemy and SQLModel.
Provides engine, session maker, and FastAPI dependency for database sessions.
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

import structlog
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool
from sqlmodel import SQLModel, create_engine

from src.core.config import settings

logger = structlog.get_logger(__name__)

# Create async engine for application use
if settings.testing:
    # Testing mode: use NullPool with no pool configuration
    engine = create_async_engine(
        str(settings.database_url),
        echo=settings.database_echo,
        poolclass=NullPool,
    )
else:
    # Production mode: use connection pooling
    engine = create_async_engine(
        str(settings.database_url),
        echo=settings.database_echo,
        pool_size=settings.database_pool_size,
        max_overflow=settings.database_max_overflow,
        pool_timeout=settings.database_pool_timeout,
        pool_pre_ping=True,  # Verify connections before using them
    )

# Create sync engine for Alembic migrations
sync_engine = create_engine(
    settings.database_url_sync,
    echo=settings.database_echo,
    pool_pre_ping=True,
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency for database sessions.

    Yields:
        AsyncSession: Database session

    Usage:
        @app.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            result = await db.execute(select(User))
            return result.scalars().all()
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error("database_session_error", error=str(e))
            raise
        finally:
            await session.close()


@asynccontextmanager
async def get_db_context() -> AsyncGenerator[AsyncSession, None]:
    """
    Context manager for database sessions (non-FastAPI usage).

    Yields:
        AsyncSession: Database session

    Usage:
        async with get_db_context() as db:
            result = await db.execute(select(User))
            users = result.scalars().all()
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error("database_context_error", error=str(e))
            raise
        finally:
            await session.close()


async def check_database_health() -> dict[str, Any]:
    """
    Check database connectivity and health.

    Returns:
        Dict with status and connection info

    Usage:
        health = await check_database_health()
        if health["status"] != "healthy":
            logger.error("database_unhealthy", **health)
    """
    try:
        async with get_db_context() as db:
            # Execute simple query
            from sqlalchemy import text

            result = await db.execute(text("SELECT 1"))
            result.scalar()

            # Get pool stats
            pool = engine.pool
            pool_status = {
                "size": pool.size(),
                "checked_in": pool.checkedin(),
                "checked_out": pool.checkedout(),
                "overflow": pool.overflow(),
            }

            return {
                "status": "healthy",
                "pool": pool_status,
                "database_url": (
                    str(settings.database_url).split("@")[1]
                    if "@" in str(settings.database_url)
                    else "unknown"
                ),  # Hide credentials
            }
    except Exception as e:
        logger.error("database_health_check_failed", error=str(e))
        return {
            "status": "unhealthy",
            "error": str(e),
        }


async def init_database() -> None:
    """
    Initialize database (for testing or first-time setup).
    Creates all tables defined in models.

    Note:
        In production, use Alembic migrations instead.
    """
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
        logger.info("database_initialized")


async def drop_database() -> None:
    """
    Drop all tables (for testing cleanup).

    Warning:
        Destructive operation! Only use in testing.
    """
    if not settings.testing:
        raise RuntimeError("drop_database can only be called in testing mode")

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
        logger.info("database_dropped")


async def close_database() -> None:
    """
    Close database connections and dispose engine.
    Call during application shutdown.
    """
    await engine.dispose()
    logger.info("database_connections_closed")
