"""
Database configuration and session management.
"""
import logging
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool
from sqlalchemy import text

from app.core.config import settings

logger = logging.getLogger(__name__)

DATABASE_URL = settings.DATABASE_URL

# Create async engine with PgBouncer-safe configuration
engine = create_async_engine(
    DATABASE_URL,
    echo=settings.DEBUG,
    connect_args={
        "statement_cache_size": 0,  # Disable prepared statements
        "server_settings": {
            "application_name": "fastapi_app",
            "jit": "off",
        }
    },
    poolclass=NullPool,  # Disable SQLAlchemy connection pooling (let PgBouncer handle it)
)

# Async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

class Base(DeclarativeBase):
    """Base class for all database models."""
    pass

async def get_db() -> AsyncSession:
    """Dependency to get a database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"Database session error: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()

async def create_tables():
    """Create all database tables with error handling."""
    try:
        # Import all models to register them with Base
        from app.models.task import Task
        from app.models.context_entry import ContextEntry
        from app.models.category import Category
        
        async with engine.begin() as conn:
            # Use raw text to avoid prepared statement issues
            await conn.execute(text("SELECT 1"))
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables created successfully")
            
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        logger.info("Continuing startup despite table creation error")

async def test_connection():
    """Test database connectivity."""
    try:
        async with engine.begin() as conn:
            # Use text() to avoid prepared statement caching
            await conn.execute(text("SELECT 1"))
            logger.info("Database connection test successful")
            return True
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        return False
