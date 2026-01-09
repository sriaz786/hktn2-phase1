"""Pydantic schemas for API request/response validation."""

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field

from app.models.todo import Priority, Status


# ==================== Todo Schemas ====================


class TodoCreate(BaseModel):
    """Schema for creating a todo item."""

    title: str = Field(..., min_length=1, max_length=200, description="Todo title")
    description: Optional[str] = Field(None, max_length=2000, description="Todo description")
    due_date: Optional[datetime] = Field(None, description="Due date for the todo")
    priority: Priority = Field(default=Priority.MEDIUM, description="Todo priority")
    tags: List[str] = Field(default_factory=list, description="Tags for the todo")

    model_config = {"json_schema_extra": {"example": {"title": "Complete project documentation", "priority": "high"}}}


class TodoUpdate(BaseModel):
    """Schema for updating a todo item."""

    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    due_date: Optional[datetime] = None
    priority: Optional[Priority] = None
    status: Optional[Status] = None
    tags: Optional[List[str]] = None

    model_config = {"json_schema_extra": {"example": {"status": "in_progress", "priority": "urgent"}}}


class TodoResponse(BaseModel):
    """Schema for todo response."""

    id: int
    title: str
    description: Optional[str]
    due_date: Optional[datetime]
    priority: Priority
    status: Status
    tags: List[str]
    created_at: datetime
    modified_at: Optional[datetime]

    model_config = {"from_attributes": True}


class TodoFilters(BaseModel):
    """Schema for filtering todos."""

    status: Optional[Status] = None
    priority: Optional[Priority] = None
    tags: Optional[List[str]] = None


class TodoSort(BaseModel):
    """Schema for sorting todos."""

    sort_by: str = Field(default="created_at", description="Field to sort by")
    sort_order: str = Field(default="desc", pattern="^(asc|desc)$", description="Sort order")


class TodoListResponse(BaseModel):
    """Schema for todo list response."""

    data: List[TodoResponse]
    metadata: dict = Field(
        default_factory=lambda: {"total": 0, "page": 1, "page_size": 50},
        description="Pagination metadata",
    )


# ==================== AI Schemas ====================


class SuggestionRequest(BaseModel):
    """Schema for AI suggestion request."""

    description: str = Field(..., min_length=1, description="Task description for suggestion")

    model_config = {"json_schema_extra": {"example": {"description": "I need to organize my project files"}}}


class SuggestionItem(BaseModel):
    """Individual suggestion item."""

    title: str
    description: str
    priority: Priority


class SuggestionResponse(BaseModel):
    """Schema for AI suggestion response."""

    suggestions: List[SuggestionItem]


class TodoSummary(BaseModel):
    """Summary of a todo for AI prioritization."""

    id: int
    title: str
    due_date: Optional[datetime]
    priority: Priority


class PrioritizationRequest(BaseModel):
    """Schema for AI prioritization request."""

    todos: List[TodoSummary] = Field(..., min_length=1, description="List of todos to prioritize")

    model_config = {
        "json_schema_extra": {
            "example": {
                "todos": [
                    {"id": 1, "title": "Fix critical bug", "due_date": "2025-01-07T00:00:00Z", "priority": "high"},
                ]
            }
        }
    }


class PrioritizedTodo(BaseModel):
    """Prioritized todo item."""

    todo_id: int
    title: str
    recommended_priority: Priority
    reasoning: str


class PrioritizationResponse(BaseModel):
    """Schema for AI prioritization response."""

    ranked_todos: List[PrioritizedTodo]


class BreakdownRequest(BaseModel):
    """Schema for AI task breakdown request."""

    task: str = Field(..., min_length=1, description="Complex task to break down")

    model_config = {"json_schema_extra": {"example": {"task": "Build a REST API with authentication"}}}


class Subtask(BaseModel):
    """Individual subtask from breakdown."""

    title: str
    estimated_order: int = Field(..., ge=1, description="Execution order")
    dependencies: List[int] = Field(default_factory=list, description="Dependency subtask IDs")


class BreakdownResponse(BaseModel):
    """Schema for AI task breakdown response."""

    subtasks: List[Subtask]


# ==================== Error Schemas ====================


class ErrorCode(str, Enum):
    """Error code enumeration."""

    VALIDATION_ERROR = "VALIDATION_ERROR"
    NOT_FOUND = "NOT_FOUND"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    AI_UNAVAILABLE = "AI_UNAVAILABLE"


class ErrorDetail(BaseModel):
    """Error detail information."""

    field: str
    message: str


class ErrorResponse(BaseModel):
    """Schema for error response."""

    error: dict = Field(
        ...,
        description="Error information",
    )
