"""
Category model for task categorization.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Integer, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.core.database import Base


class Category(Base):
    """
    Model for task categories with usage tracking.
    
    This model stores categories that can be used to classify tasks,
    with tracking of usage frequency for AI recommendations.
    """
    __tablename__ = "categories"
    
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    
    name = Column(
        String(100),
        unique=True,
        nullable=False,
        index=True
    )
    
    description = Column(
        Text,
        default=""
    )
    
    usage_frequency = Column(
        Integer,
        default=0,
        index=True
    )
    
    color = Column(
        String(7),
        default="#3B82F6"
    )
    
    is_active = Column(
        Boolean,
        default=True,
        index=True
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
        return f"<Category(id={self.id}, name='{self.name}', usage={self.usage_frequency})>"
    
    def increment_usage(self):
        """Increment the usage frequency of this category."""
        self.usage_frequency += 1
    
    def decrement_usage(self):
        """Decrement the usage frequency of this category."""
        if self.usage_frequency > 0:
            self.usage_frequency -= 1