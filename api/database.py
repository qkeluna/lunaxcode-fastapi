"""Database connection and session management using async SQLAlchemy"""

import re
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from typing import AsyncGenerator

from api.config import settings

# Base class for ORM models
Base = declarative_base()

# Convert DATABASE_URL to async format
database_url = settings.DATABASE_URL

# Remove problematic query parameters that asyncpg doesn't support
database_url = re.sub(r'[?&]sslmode=[^&]*', '', database_url)
database_url = re.sub(r'[?&]channel_binding=[^&]*', '', database_url)

# Convert to async format
database_url = re.sub(r'^postgresql:', 'postgresql+asyncpg:', database_url)

# Create async SQLAlchemy engine
engine = create_async_engine(
    database_url,
    echo=False if settings.is_production else True,  # Log SQL in development
    future=True,
    pool_pre_ping=True,  # Verify connections before using
    pool_recycle=300,    # Recycle connections after 5 minutes
    pool_size=5,         # Connection pool size
    max_overflow=10,     # Max overflow connections
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency function to get async database session.
    Ensures session is closed after request.

    Usage in FastAPI routes:
        @router.get("/example")
        async def example(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """Initialize database tables (for development/testing)"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    """Close database connections"""
    await engine.dispose()