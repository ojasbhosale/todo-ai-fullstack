"""
Database configuration and session management.
"""
import logging
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

logger = logging.getLogger(__name__)

DATABASE_URL = settings.DATABASE_URL

# Create async engine with complete prepared statement disabling for pgbouncer
engine = create_async_engine(
    DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_recycle=300,
    # Complete asyncpg configuration for pgbouncer compatibility
    connect_args={
        "statement_cache_size": 0,
        "prepared_statement_cache_size": 0,
        "prepared_statement_name_func": None,
        "server_settings": {
            "application_name": "fastapi_app",
            "jit": "off",
        }
    },
    # Additional engine configuration for stability
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

class Base(DeclarativeBase):
    """Base class for all database models."""
    pass

async def get_db() -> AsyncSession:
    """Dependency to get database session."""
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
        # Import all models to ensure they're registered
        from app.models.task import Task
        from app.models.context_entry import ContextEntry
        from app.models.category import Category
        
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables created successfully")
            
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        # Don't raise the exception to prevent startup failure
        # Tables might already exist or be created by migrations
        logger.info("Continuing startup despite table creation error")

async def test_connection():
    """Test database connectivity."""
    try:
        async with engine.begin() as conn:
            result = await conn.execute("SELECT 1")
            logger.info("Database connection test successful")
            return True
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        return False