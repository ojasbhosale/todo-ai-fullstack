"""
Pydantic schemas for Task model.
"""
from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field


class TaskBase(BaseModel):
    """Base task schema with common fields."""
    title: str = Field(..., max_length=200, description="Task title")
    description: Optional[str] = Field("", description="Task description")
    category: Optional[str] = Field("", max_length=100, description="Task category")
    priority_score: int = Field(5, ge=1, le=10, description="Priority score (1-10)")
    deadline: Optional[datetime] = Field(None, description="Task deadline")
    status: str = Field("pending", description="Task status")


class TaskCreate(TaskBase):
    """Schema for creating a new task."""
    pass


class TaskUpdate(BaseModel):
    """Schema for updating a task."""
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=100)
    priority_score: Optional[int] = Field(None, ge=1, le=10)
    deadline: Optional[datetime] = None
    status: Optional[str] = None
    ai_enhanced_description: Optional[str] = None
    ai_suggested_tags: Optional[List[str]] = None
    context_references: Optional[List[str]] = None


class TaskResponse(TaskBase):
    """Schema for task response."""
    id: UUID
    ai_enhanced_description: str
    ai_suggested_tags: List[str]
    context_references: List[str]
    is_overdue: bool
    priority_label: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class AITaskSuggestionRequest(BaseModel):
    """Schema for AI task suggestion requests."""
    title: str = Field(..., max_length=200)
    description: Optional[str] = Field("", description="Task description")
    category: Optional[str] = Field("", max_length=100)
    context_data: Optional[List[dict]] = Field([], description="Context data for AI analysis")
    user_preferences: Optional[dict] = Field({}, description="User preferences")
    current_workload: Optional[int] = Field(0, description="Current number of pending tasks")


class AITaskSuggestionResponse(BaseModel):
    """Schema for AI task suggestion responses."""
    priority_score: int = Field(..., ge=1, le=10)
    suggested_deadline: Optional[datetime]
    enhanced_description: str
    suggested_category: str
    ai_suggested_tags: List[str]
    reasoning: str
    estimated_duration: str
    context_insights: List[str]


class TaskStatistics(BaseModel):
    """Schema for task statistics."""
    total_tasks: int
    pending_tasks: int
    in_progress_tasks: int
    completed_tasks: int
    overdue_tasks: int
    high_priority_tasks: int
    categories: List[str]
    average_priority: float