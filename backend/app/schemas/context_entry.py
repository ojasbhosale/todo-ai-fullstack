"""
Pydantic schemas for ContextEntry model.
"""
from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field


class ContextEntryBase(BaseModel):
    """Base context entry schema."""
    content: str = Field(..., description="Context content")
    source_type: str = Field(..., description="Source type (email, whatsapp, notes, etc.)")
    meta_data: Optional[dict] = Field({}, description="Additional meta_data")


class ContextEntryCreate(ContextEntryBase):
    """Schema for creating a new context entry."""
    pass


class ContextEntryUpdate(BaseModel):
    """Schema for updating a context entry."""
    content: Optional[str] = None
    source_type: Optional[str] = None
    meta_data: Optional[dict] = None
    processed_insights: Optional[dict] = None
    is_processed: Optional[bool] = None
    relevance_score: Optional[float] = None
    extracted_keywords: Optional[List[str]] = None


class ContextEntryResponse(ContextEntryBase):
    """Schema for context entry response."""
    id: UUID
    processed_insights: dict
    is_processed: bool
    relevance_score: float
    extracted_keywords: List[str]
    content_preview: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class ContextAnalysisRequest(BaseModel):
    """Schema for context analysis requests."""
    content: str = Field(..., description="Content to analyze")
    source_type: str = Field(..., description="Source type")
    analyze_sentiment: bool = Field(True, description="Whether to analyze sentiment")
    extract_keywords: bool = Field(True, description="Whether to extract keywords")
    calculate_relevance: bool = Field(True, description="Whether to calculate relevance")


class ContextAnalysisResponse(BaseModel):
    """Schema for context analysis responses."""
    extracted_keywords: List[str]
    relevance_score: float
    sentiment: str
    insights: List[str]