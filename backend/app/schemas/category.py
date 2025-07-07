"""
Pydantic schemas for Category model.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field


class CategoryBase(BaseModel):
    """Base category schema."""
    name: str = Field(..., max_length=100, description="Category name")
    description: Optional[str] = Field("", description="Category description")
    color: str = Field("#3B82F6", description="Category color (hex format)")
    is_active: bool = Field(True, description="Whether category is active")


class CategoryCreate(CategoryBase):
    """Schema for creating a new category."""
    pass


class CategoryUpdate(BaseModel):
    """Schema for updating a category."""
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    color: Optional[str] = None
    is_active: Optional[bool] = None


class CategoryResponse(CategoryBase):
    """Schema for category response."""
    id: UUID
    usage_frequency: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class CategoryStatistics(BaseModel):
    """Schema for category statistics."""
    total_categories: int
    active_categories: int
    most_used_category: str
    least_used_category: str
    average_usage: float