"""
Context Entry API endpoints.
"""
import logging
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models.context_entry import ContextEntry
from app.schemas.context_entry import (
    ContextEntryCreate, ContextEntryUpdate, ContextEntryResponse,
    ContextAnalysisRequest, ContextAnalysisResponse
)
from app.services.ai_service import ContextAnalyzer

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/", response_model=List[ContextEntryResponse])
async def get_context_entries(
    source_type: Optional[str] = Query(None, description="Filter by source type"),
    is_processed: Optional[bool] = Query(None, description="Filter by processing status"),
    min_relevance: Optional[float] = Query(None, ge=0.0, le=1.0, description="Minimum relevance score"),
    skip: int = Query(0, ge=0, description="Number of entries to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of entries to return"),
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve all context entries with optional filtering.
    """
    try:
        query = select(ContextEntry)
        
        # Apply filters
        if source_type:
            query = query.where(ContextEntry.source_type == source_type)
        
        if is_processed is not None:
            query = query.where(ContextEntry.is_processed == is_processed)
        
        if min_relevance is not None:
            query = query.where(ContextEntry.relevance_score >= min_relevance)
        
        # Apply pagination and ordering
        query = query.order_by(ContextEntry.created_at.desc())
        query = query.offset(skip).limit(limit)
        
        result = await db.execute(query)
        entries = result.scalars().all()
        
        return entries
        
    except Exception as e:
        logger.error(f"Error retrieving context entries: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve context entries")


@router.post("/", response_model=ContextEntryResponse)
async def create_context_entry(
    entry: ContextEntryCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new context entry.
    """
    try:
        # Analyze the content
        analyzer = ContextAnalyzer()
        keywords = analyzer.extract_keywords(entry.content)
        relevance_score = analyzer.calculate_relevance_score(entry.content)
        sentiment = analyzer.analyze_sentiment(entry.content)
        insights = analyzer.extract_insights(entry.content, entry.source_type)
        
        # Create the entry
        db_entry = ContextEntry(
            content=entry.content,
            source_type=entry.source_type,
            meta_data=entry.meta_data,
            extracted_keywords=keywords,
            relevance_score=relevance_score,
            processed_insights={
                "sentiment": sentiment,
                "insights": insights
            },
            is_processed=True
        )
        
        db.add(db_entry)
        await db.commit()
        await db.refresh(db_entry)
        
        logger.info(f"Context entry created: {db_entry.source_type} (ID: {db_entry.id})")
        return db_entry
        
    except Exception as e:
        logger.error(f"Error creating context entry: {str(e)}")
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create context entry")


@router.get("/{entry_id}", response_model=ContextEntryResponse)
async def get_context_entry(
    entry_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve a specific context entry by ID.
    """
    try:
        result = await db.execute(select(ContextEntry).where(ContextEntry.id == entry_id))
        entry = result.scalar_one_or_none()
        
        if not entry:
            raise HTTPException(status_code=404, detail="Context entry not found")
        
        return entry
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving context entry {entry_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve context entry")


@router.put("/{entry_id}", response_model=ContextEntryResponse)
async def update_context_entry(
    entry_id: UUID,
    entry_update: ContextEntryUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update a specific context entry.
    """
    try:
        result = await db.execute(select(ContextEntry).where(ContextEntry.id == entry_id))
        entry = result.scalar_one_or_none()
        
        if not entry:
            raise HTTPException(status_code=404, detail="Context entry not found")
        
        # Update fields
        update_data = entry_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(entry, field, value)
        
        await db.commit()
        await db.refresh(entry)
        
        logger.info(f"Context entry updated: {entry.source_type} (ID: {entry.id})")
        return entry
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating context entry {entry_id}: {str(e)}")
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update context entry")


@router.delete("/{entry_id}")
async def delete_context_entry(
    entry_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a specific context entry.
    """
    try:
        result = await db.execute(select(ContextEntry).where(ContextEntry.id == entry_id))
        entry = result.scalar_one_or_none()
        
        if not entry:
            raise HTTPException(status_code=404, detail="Context entry not found")
        
        await db.delete(entry)
        await db.commit()
        
        logger.info(f"Context entry deleted: {entry.source_type} (ID: {entry.id})")
        return {"message": "Context entry deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting context entry {entry_id}: {str(e)}")
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete context entry")


@router.post("/analyze/", response_model=ContextAnalysisResponse)
async def analyze_context(request: ContextAnalysisRequest):
    """
    Analyze context content using AI.
    """
    try:
        analyzer = ContextAnalyzer()
        
        # Perform analysis
        keywords = analyzer.extract_keywords(request.content) if request.extract_keywords else []
        relevance_score = analyzer.calculate_relevance_score(request.content) if request.calculate_relevance else 0.0
        sentiment = analyzer.analyze_sentiment(request.content) if request.analyze_sentiment else "neutral"
        insights = analyzer.extract_insights(request.content, request.source_type)
        
        return ContextAnalysisResponse(
            extracted_keywords=keywords,
            relevance_score=relevance_score,
            sentiment=sentiment,
            insights=insights
        )
        
    except Exception as e:
        logger.error(f"Error analyzing context: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze context: {str(e)}"
        )