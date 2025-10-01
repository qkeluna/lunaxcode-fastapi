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

# Validate DATABASE_URL is set
if not database_url:
    raise ValueError(
        "DATABASE_URL environment variable is required. "
        "Please set it in Vercel dashboard or .env file."
    )

# Clean up URL for asyncpg compatibility
# Remove problematic parameters that asyncpg doesn't support
database_url = re.sub(r'[?&]channel_binding=[^&]*', '', database_url)
database_url = re.sub(r'[?&]sslmode=[^&]*', '', database_url)

# Convert to async format (postgresql -> postgresql+asyncpg)
if database_url.startswith('postgresql://'):
    database_url = database_url.replace('postgresql://', 'postgresql+asyncpg://', 1)
elif database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql+asyncpg://', 1)

# Add SSL requirement for asyncpg (Neon requires SSL)
# asyncpg uses ssl=require instead of sslmode=require
if '?' in database_url:
    database_url += '&ssl=require'
else:
    database_url += '?ssl=require'

# Create async SQLAlchemy engine
# For Vercel serverless: use smaller pool or NullPool
if settings.is_production:
    # Serverless: minimal pooling
    from sqlalchemy.pool import NullPool
    engine = create_async_engine(
        database_url,
        echo=False,
        future=True,
        poolclass=NullPool,  # No pooling for serverless
    )
else:
    # Development: normal pooling
    engine = create_async_engine(
        database_url,
        echo=True,
        future=True,
        pool_pre_ping=True,
        pool_recycle=300,
        pool_size=5,
        max_overflow=10,
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