"""Database session factory."""

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from policymind.core.config import Settings


def create_engine_and_sessionmaker(
    settings: Settings,
) -> tuple[AsyncEngine, async_sessionmaker[AsyncSession]]:
    """Build an async engine and session factory from settings."""
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=settings.DEBUG,
        pool_size=5,
        max_overflow=10,
    )
    sessionmaker = async_sessionmaker(engine, expire_on_commit=False)
    return engine, sessionmaker
