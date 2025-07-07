"""
Category API endpoints.
"""
import logging
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.models.category import Category
from app.schemas.category import (
    CategoryCreate, CategoryUpdate, CategoryResponse, CategoryStatistics
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/", response_model=List[CategoryResponse])
async def get_categories(
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    min_usage: Optional[int] = Query(None, ge=0, description="Minimum usage frequency"),
    search: Optional[str] = Query(None, description="Search categories by name"),
    skip: int = Query(0, ge=0, description="Number of categories to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of categories to return"),
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve all categories with optional filtering.
    """
    try:
        query = select(Category)
        
        # Apply filters
        if is_active is not None:
            query = query.where(Category.is_active == is_active)
        
        if min_usage is not None:
            query = query.where(Category.usage_frequency >= min_usage)
        
        if search:
            query = query.where(Category.name.ilike(f"%{search}%"))
        
        # Apply pagination and ordering
        query = query.order_by(Category.usage_frequency.desc(), Category.name)
        query = query.offset(skip).limit(limit)
        
        result = await db.execute(query)
        categories = result.scalars().all()
        
        return categories
        
    except Exception as e:
        logger.error(f"Error retrieving categories: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve categories")


@router.post("/", response_model=CategoryResponse)
async def create_category(
    category: CategoryCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new category.
    """
    try:
        # Check if category name already exists
        result = await db.execute(select(Category).where(Category.name == category.name))
        existing_category = result.scalar_one_or_none()
        
        if existing_category:
            raise HTTPException(status_code=400, detail="Category name already exists")
        
        db_category = Category(**category.model_dump())
        db.add(db_category)
        await db.commit()
        await db.refresh(db_category)
        
        logger.info(f"Category created: {db_category.name} (ID: {db_category.id})")
        return db_category
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating category: {str(e)}")
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create category")


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve a specific category by ID.
    """
    try:
        result = await db.execute(select(Category).where(Category.id == category_id))
        category = result.scalar_one_or_none()
        
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        
        return category
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving category {category_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve category")


@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: UUID,
    category_update: CategoryUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update a specific category.
    """
    try:
        result = await db.execute(select(Category).where(Category.id == category_id))
        category = result.scalar_one_or_none()
        
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        
        # Check if new name already exists (if name is being updated)
        if category_update.name and category_update.name != category.name:
            result = await db.execute(select(Category).where(Category.name == category_update.name))
            existing_category = result.scalar_one_or_none()
            if existing_category:
                raise HTTPException(status_code=400, detail="Category name already exists")
        
        # Update fields
        update_data = category_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(category, field, value)
        
        await db.commit()
        await db.refresh(category)
        
        logger.info(f"Category updated: {category.name} (ID: {category.id})")
        return category
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating category {category_id}: {str(e)}")
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update category")


@router.delete("/{category_id}")
async def delete_category(
    category_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a specific category.
    """
    try:
        result = await db.execute(select(Category).where(Category.id == category_id))
        category = result.scalar_one_or_none()
        
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        
        await db.delete(category)
        await db.commit()
        
        logger.info(f"Category deleted: {category.name} (ID: {category.id})")
        return {"message": "Category deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting category {category_id}: {str(e)}")
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete category")


@router.get("/statistics/", response_model=CategoryStatistics)
async def get_category_statistics(db: AsyncSession = Depends(get_db)):
    """
    Get category statistics and analytics.
    """
    try:
        # Get basic counts
        total_categories = await db.scalar(select(func.count(Category.id)))
        active_categories = await db.scalar(
            select(func.count(Category.id)).where(Category.is_active == True)
        )
        
        # Get most and least used categories
        most_used_result = await db.execute(
            select(Category.name)
            .where(Category.usage_frequency > 0)
            .order_by(Category.usage_frequency.desc())
            .limit(1)
        )
        most_used = most_used_result.scalar_one_or_none() or "N/A"
        
        least_used_result = await db.execute(
            select(Category.name)
            .where(Category.usage_frequency > 0)
            .order_by(Category.usage_frequency.asc())
            .limit(1)
        )
        least_used = least_used_result.scalar_one_or_none() or "N/A"
        
        # Get average usage
        avg_usage = await db.scalar(select(func.avg(Category.usage_frequency))) or 0
        
        return CategoryStatistics(
            total_categories=total_categories or 0,
            active_categories=active_categories or 0,
            most_used_category=most_used,
            least_used_category=least_used,
            average_usage=round(float(avg_usage), 2)
        )
        
    except Exception as e:
        logger.error(f"Error generating category statistics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate statistics")


@router.get("/popular/", response_model=List[CategoryResponse])
async def get_popular_categories(
    limit: int = Query(10, ge=1, le=50, description="Number of popular categories to return"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get most popular categories based on usage frequency.
    """
    try:
        query = select(Category).where(
            Category.usage_frequency > 0,
            Category.is_active == True
        ).order_by(Category.usage_frequency.desc()).limit(limit)
        
        result = await db.execute(query)
        categories = result.scalars().all()
        
        return categories
        
    except Exception as e:
        logger.error(f"Error retrieving popular categories: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve popular categories")