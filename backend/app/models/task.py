"""
Task model for the Smart Todo List application.
"""
import uuid
from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, String, Text, Integer, DateTime, Boolean, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.core.database import Base


class Task(Base):
    """
    Task model with AI-enhanced features.
    
    This model stores task information including AI-generated priority scores,
    deadline suggestions, and enhanced descriptions.
    """
    __tablename__ = "tasks"
    
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    
    title = Column(
        String(200),
        nullable=False,
        index=True
    )
    
    description = Column(
        Text,
        default=""
    )
    
    category = Column(
        String(100),
        default="",
        index=True
    )
    
    priority_score = Column(
        Integer,
        default=5,
        index=True
    )
    
    deadline = Column(
        DateTime(timezone=True),
        nullable=True,
        index=True
    )
    
    status = Column(
        String(20),
        default="pending",
        index=True
    )
    
    ai_enhanced_description = Column(
        Text,
        default=""
    )
    
    ai_suggested_tags = Column(
        JSON,
        default=list
    )
    
    context_references = Column(
        JSON,
        default=list
    )
    
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    
    def __repr__(self):
        return f"<Task(id={self.id}, title='{self.title}', priority={self.priority_score})>"
    
    @property
    def is_overdue(self) -> bool:
        """Check if task is overdue."""
        if self.deadline and self.status not in ['completed', 'cancelled']:
            return datetime.utcnow() > self.deadline.replace(tzinfo=None)
        return False
    
    @property
    def priority_label(self) -> str:
        """Get human-readable priority label."""
        priority_labels = {
            1: "Very Low", 2: "Low", 3: "Medium-Low", 4: "Medium", 5: "Medium-High",
            6: "High", 7: "Very High", 8: "Critical", 9: "Urgent", 10: "Emergency"
        }
        return priority_labels.get(self.priority_score, "Unknown")