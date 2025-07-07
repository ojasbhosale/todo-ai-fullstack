"""
Supabase setup script for creating tables and Row Level Security (RLS) policies.

This script helps set up the required database tables and security policies
for the Smart Todo List application in Supabase using FastAPI models.
"""
import asyncio
import logging
from sqlalchemy.ext.asyncio import create_async_engine
from app.core.config import settings
from app.core.database import Base
from app.models.task import Task
from app.models.context_entry import ContextEntry
from app.models.category import Category

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def create_tables():
    """Create all database tables."""
    try:
        # Convert PostgreSQL URL to async version
        database_url = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
        
        engine = create_async_engine(database_url, echo=True)
        
        async with engine.begin() as conn:
            # Create all tables
            await conn.run_sync(Base.metadata.create_all)
            logger.info("✅ All tables created successfully!")
        
        await engine.dispose()
        
    except Exception as e:
        logger.error(f"❌ Error creating tables: {e}")
        raise


async def create_sample_data():
    """Create sample data for testing."""
    try:
        from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
        
        database_url = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
        engine = create_async_engine(database_url)
        AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        
        async with AsyncSessionLocal() as session:
            # Create sample categories
            categories_data = [
                {"name": "Work", "description": "Work-related tasks", "color": "#3B82F6", "usage_frequency": 5},
                {"name": "Personal", "description": "Personal tasks and activities", "color": "#10B981", "usage_frequency": 3},
                {"name": "Shopping", "description": "Shopping and errands", "color": "#F59E0B", "usage_frequency": 2},
                {"name": "Health", "description": "Health and fitness related", "color": "#EF4444", "usage_frequency": 1},
                {"name": "Learning", "description": "Learning and education", "color": "#8B5CF6", "usage_frequency": 4}
            ]
            
            for cat_data in categories_data:
                category = Category(**cat_data)
                session.add(category)
            
            # Create sample context entries
            context_data = [
                {
                    "content": "Meeting with client tomorrow at 3 PM to discuss project requirements",
                    "source_type": "email",
                    "relevance_score": 0.8,
                    "extracted_keywords": ["meeting", "client", "project"],
                    "processed_insights": {"sentiment": "neutral", "insights": ["Contains meeting information"]},
                    "is_processed": True
                },
                {
                    "content": "Reminder: Doctor appointment on Friday",
                    "source_type": "whatsapp",
                    "relevance_score": 0.6,
                    "extracted_keywords": ["doctor", "appointment", "friday"],
                    "processed_insights": {"sentiment": "neutral", "insights": ["Health-related reminder"]},
                    "is_processed": True
                },
                {
                    "content": "Need to buy groceries this weekend",
                    "source_type": "notes",
                    "relevance_score": 0.4,
                    "extracted_keywords": ["groceries", "shopping", "weekend"],
                    "processed_insights": {"sentiment": "neutral", "insights": ["Shopping task"]},
                    "is_processed": True
                }
            ]
            
            for ctx_data in context_data:
                context_entry = ContextEntry(**ctx_data)
                session.add(context_entry)
            
            # Create sample tasks
            tasks_data = [
                {
                    "title": "Complete project report",
                    "description": "Finish the quarterly project report with all metrics",
                    "category": "Work",
                    "priority_score": 8,
                    "status": "pending",
                    "ai_enhanced_description": "High priority task: Complete quarterly project report including performance metrics, budget analysis, and future recommendations.",
                    "ai_suggested_tags": ["report", "quarterly", "deadline", "work"]
                },
                {
                    "title": "Buy groceries",
                    "description": "Weekly grocery shopping for household items",
                    "category": "Shopping",
                    "priority_score": 4,
                    "status": "pending",
                    "ai_enhanced_description": "Regular weekly task: Purchase groceries and household essentials.",
                    "ai_suggested_tags": ["groceries", "shopping", "weekly"]
                },
                {
                    "title": "Schedule doctor appointment",
                    "description": "Book annual health checkup",
                    "category": "Health",
                    "priority_score": 6,
                    "status": "pending",
                    "ai_enhanced_description": "Important health maintenance: Schedule annual physical examination and health screening.",
                    "ai_suggested_tags": ["doctor", "health", "checkup", "appointment"]
                }
            ]
            
            for task_data in tasks_data:
                task = Task(**task_data)
                session.add(task)
            
            await session.commit()
            logger.info("✅ Sample data created successfully!")
        
        await engine.dispose()
        
    except Exception as e:
        logger.error(f"❌ Error creating sample data: {e}")
        raise


async def main():
    """Main setup function."""
    print("🚀 Setting up Supabase database for Smart Todo List (FastAPI)...")
    print("=" * 60)
    
    try:
        # Step 1: Create tables
        print("📋 Creating tables...")
        await create_tables()
        
        # Step 2: Create sample data
        print("\n📝 Creating sample data...")
        await create_sample_data()
        
        print("\n✅ Database setup completed!")
        print("\nNext steps:")
        print("1. Start the FastAPI server: uvicorn main:app --reload")
        print("2. Visit the API docs: http://localhost:8000/docs")
        print("3. Test the endpoints:")
        print("   - Tasks: http://localhost:8000/api/v1/tasks/")
        print("   - Context: http://localhost:8000/api/v1/context/")
        print("   - Categories: http://localhost:8000/api/v1/categories/")
        print("   - AI Suggestions: http://localhost:8000/api/v1/tasks/ai-suggestions/")
        
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())