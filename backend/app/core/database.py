import logging
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool
from sqlalchemy import text

from app.core.config import settings

logger = logging.getLogger(__name__)

DATABASE_URL = settings.DATABASE_URL

# Create async engine - fully PgBouncer compatible
engine = create_async_engine(
    DATABASE_URL,
    echo=settings.DEBUG,
    connect_args={
        "statement_cache_size": 0,  # Disable asyncpg statement caching
        "server_settings": {
            "application_name": "fastapi_app",
            "jit": "off",
        },
    },
    poolclass=NullPool,  # Disable SQLAlchemy's own pooling
    hide_parameters=True,  # Hides parameters in logs (security + avoids version checks)
)

# Async session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

class Base(DeclarativeBase):
    """Base class for all models."""
    pass

async def get_db() -> AsyncSession:
    """Yield an async database session."""
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
    """Create all tables safely, without prepared statements."""
    try:
        from app.models.task import Task
        from app.models.context_entry import ContextEntry
        from app.models.category import Category

        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))  # Simple safe query
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating tables: {e}")
        logger.info("Continuing startup despite error")

async def test_connection():
    """Test DB connection with PgBouncer-safe query."""
    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
            logger.info("Database connection test passed")
            return True
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        return False
