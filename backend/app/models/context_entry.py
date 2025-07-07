"""
Context entry model for storing daily context data.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, Boolean, Float, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.core.database import Base


class ContextEntry(Base):
    """
    Model for storing daily context entries (messages, emails, notes).
    
    This model captures various types of context that can be used by AI
    to provide better task suggestions and prioritization.
    """
    __tablename__ = "context_entries"
    
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    
    content = Column(
        Text,
        nullable=False
    )
    
    source_type = Column(
        String(20),
        nullable=False,
        index=True
    )
    
    processed_insights = Column(
        JSON,
        default=dict
    )
    
    meta_data = Column(
    JSON,
    default=dict
    )

    is_processed = Column(
        Boolean,
        default=False,
        index=True
    )
    
    relevance_score = Column(
        Float,
        default=0.0,
        index=True
    )
    
    extracted_keywords = Column(
        JSON,
        default=list
    )
    
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True
    )
    
    def __repr__(self):
        return f"<ContextEntry(id={self.id}, source_type='{self.source_type}')>"
    
    @property
    def content_preview(self) -> str:
        """Return a short preview of the content."""
        return self.content[:100] + "..." if len(self.content) > 100 else self.content