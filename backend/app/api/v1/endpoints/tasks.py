"""
Task API endpoints.
"""
import logging
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from datetime import datetime

from app.core.database import get_db
from app.models.task import Task
from app.schemas.task import (
    TaskCreate, TaskUpdate, TaskResponse, TaskStatistics,
    AITaskSuggestionRequest, AITaskSuggestionResponse
)
from app.services.ai_service import AITaskProcessor

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/", response_model=List[TaskResponse])
async def get_tasks(
    status: Optional[str] = Query(None, description="Filter by status"),
    category: Optional[str] = Query(None, description="Filter by category"),
    priority: Optional[int] = Query(None, ge=1, le=10, description="Filter by priority"),
    overdue: Optional[bool] = Query(None, description="Filter overdue tasks"),
    skip: int = Query(0, ge=0, description="Number of tasks to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of tasks to return"),
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve all tasks with optional filtering.
    """
    try:
        query = select(Task)
        
        # Apply filters
        if status:
            query = query.where(Task.status == status)
        
        if category:
            query = query.where(Task.category.ilike(f"%{category}%"))
        
        if priority:
            query = query.where(Task.priority_score == priority)
        
        if overdue:
            query = query.where(
                and_(
                    Task.deadline < datetime.utcnow(),
                    Task.status.in_(["pending", "in_progress"])
                )
            )
        
        # Apply pagination and ordering
        query = query.order_by(Task.priority_score.desc(), Task.created_at.desc())
        query = query.offset(skip).limit(limit)
        
        result = await db.execute(query)
        tasks = result.scalars().all()
        
        return tasks
        
    except Exception as e:
        logger.error(f"Error retrieving tasks: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve tasks")


@router.post("/", response_model=TaskResponse)
async def create_task(
    task: TaskCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new task.
    """
    try:
        db_task = Task(**task.model_dump())
        db.add(db_task)
        await db.commit()
        await db.refresh(db_task)
        
        logger.info(f"Task created: {db_task.title} (ID: {db_task.id})")
        return db_task
        
    except Exception as e:
        logger.error(f"Error creating task: {str(e)}")
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create task")


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve a specific task by ID.
    """
    try:
        result = await db.execute(select(Task).where(Task.id == task_id))
        task = result.scalar_one_or_none()
        
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        return task
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving task {task_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve task")


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: UUID,
    task_update: TaskUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update a specific task.
    """
    try:
        result = await db.execute(select(Task).where(Task.id == task_id))
        task = result.scalar_one_or_none()
        
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        # Update fields
        update_data = task_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(task, field, value)
        
        await db.commit()
        await db.refresh(task)
        
        logger.info(f"Task updated: {task.title} (ID: {task.id})")
        return task
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating task {task_id}: {str(e)}")
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update task")


@router.delete("/{task_id}")
async def delete_task(
    task_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a specific task.
    """
    try:
        result = await db.execute(select(Task).where(Task.id == task_id))
        task = result.scalar_one_or_none()
        
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        await db.delete(task)
        await db.commit()
        
        logger.info(f"Task deleted: {task.title} (ID: {task.id})")
        return {"message": "Task deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting task {task_id}: {str(e)}")
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete task")


@router.post("/ai-suggestions/", response_model=AITaskSuggestionResponse)
async def get_ai_task_suggestions(
    request: AITaskSuggestionRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Generate AI-powered task suggestions.
    """
    try:
        ai_processor = AITaskProcessor()
        
        suggestions = await ai_processor.generate_task_suggestions(
            title=request.title,
            description=request.description,
            category=request.category,
            context_data=request.context_data,
            user_preferences=request.user_preferences,
            current_workload=request.current_workload
        )
        
        logger.info(f"AI suggestions generated for task: {request.title}")
        return suggestions
        
    except Exception as e:
        logger.error(f"Error generating AI suggestions: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate AI suggestions: {str(e)}"
        )


@router.get("/statistics/", response_model=TaskStatistics)
async def get_task_statistics(db: AsyncSession = Depends(get_db)):
    """
    Get task statistics and analytics.
    """
    try:
        # Get basic counts
        total_tasks = await db.scalar(select(func.count(Task.id)))
        pending_tasks = await db.scalar(
            select(func.count(Task.id)).where(Task.status == "pending")
        )
        in_progress_tasks = await db.scalar(
            select(func.count(Task.id)).where(Task.status == "in_progress")
        )
        completed_tasks = await db.scalar(
            select(func.count(Task.id)).where(Task.status == "completed")
        )
        
        # Get overdue tasks
        overdue_tasks = await db.scalar(
            select(func.count(Task.id)).where(
                and_(
                    Task.deadline < datetime.utcnow(),
                    Task.status.in_(["pending", "in_progress"])
                )
            )
        )
        
        # Get high priority tasks
        high_priority_tasks = await db.scalar(
            select(func.count(Task.id)).where(Task.priority_score >= 7)
        )
        
        # Get categories
        result = await db.execute(
            select(Task.category).distinct().where(Task.category != "")
        )
        categories = [row[0] for row in result.fetchall()]
        
        # Get average priority
        avg_priority = await db.scalar(select(func.avg(Task.priority_score))) or 0
        
        return TaskStatistics(
            total_tasks=total_tasks or 0,
            pending_tasks=pending_tasks or 0,
            in_progress_tasks=in_progress_tasks or 0,
            completed_tasks=completed_tasks or 0,
            overdue_tasks=overdue_tasks or 0,
            high_priority_tasks=high_priority_tasks or 0,
            categories=categories,
            average_priority=round(float(avg_priority), 2)
        )
        
    except Exception as e:
        logger.error(f"Error generating task statistics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate statistics")