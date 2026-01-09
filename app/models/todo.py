"""Todo database model and enums."""

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import Field
from sqlmodel import Column, DateTime, Index, SQLModel, Text, func


class Priority(str, Enum):
    """Todo priority levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Status(str, Enum):
    """Todo status values."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Todo(SQLModel, table=True):
    """Todo item entity."""

    __tablename__ = "todos"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(min_length=1, max_length=200, description="Todo title")
    description: Optional[str] = Field(default=None, max_length=2000, sa_column=Column(Text))
    due_date: Optional[datetime] = Field(default=None)
    priority: Priority = Field(default=Priority.MEDIUM)
    status: Status = Field(default=Status.PENDING)
    tags: List[str] = Field(default_factory=list, sa_column=Column(Text))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    modified_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    is_deleted: bool = Field(default=False)

    # Indexes for performance
    __table_args__ = (
        Index("idx_status", "status"),
        Index("idx_priority", "priority"),
        Index("idx_due_date", "due_date"),
        Index("idx_is_deleted", "is_deleted"),
    )
