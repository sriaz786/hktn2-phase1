"""Todo API endpoints."""

import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session

from app.database import get_db_session
from app.models.schemas import (
    TodoCreate,
    TodoFilters,
    TodoListResponse,
    TodoResponse,
    TodoSort,
    TodoUpdate,
)
from app.models.todo import Priority, Status
from app.repository.todo_repository import TodoRepository
from app.services.todo_service import TodoNotFoundError, TodoService

logger = logging.getLogger(__name__)

# Create router
router = APIRouter()


def get_todo_service(session: Session = Depends(get_db_session)) -> TodoService:
    """Get TodoService instance.

    Args:
        session: Database session

    Returns:
        TodoService instance
    """
    repository = TodoRepository(session)
    return TodoService(repository)


@router.post(
    "/todos",
    response_model=TodoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Todo",
    description="Create a new todo item",
)
async def create_todo(
    todo_data: TodoCreate,
    todo_service: TodoService = Depends(get_todo_service),
) -> TodoResponse:
    """Create a new todo item.

    Args:
        todo_data: Todo creation data
        todo_service: Todo service instance

    Returns:
        Created todo response

    Raises:
        HTTPException: If creation fails
    """
    logger.info("Creating todo: %s", todo_data.title)

    try:
        todo = todo_service.create_todo(todo_data)
        return todo
    except Exception as e:
        logger.exception("Failed to create todo: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create todo",
        ) from e


@router.get(
    "/todos",
    response_model=TodoListResponse,
    summary="List Todos",
    description="Get all todos with optional filtering and sorting",
)
async def list_todos(
    status_filter: Optional[Status] = Query(None, description="Filter by status"),
    priority_filter: Optional[Priority] = Query(None, description="Filter by priority"),
    tags_filter: Optional[List[str]] = Query(None, description="Filter by tags"),
    sort_by: str = Query("created_at", description="Field to sort by"),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="Sort order"),
    todo_service: TodoService = Depends(get_todo_service),
) -> TodoListResponse:
    """List all todos with optional filtering and sorting.

    Args:
        status_filter: Optional status filter
        priority_filter: Optional priority filter
        tags_filter: Optional tags filter
        sort_by: Field to sort by
        sort_order: Sort order (asc or desc)
        todo_service: Todo service instance

    Returns:
        Todo list response with metadata
    """
    logger.debug(
        "Listing todos with filters: status=%s, priority=%s, tags=%s, sort=%s %s",
        status_filter,
        priority_filter,
        tags_filter,
        sort_by,
        sort_order,
    )

    filters = None
    if status_filter or priority_filter or tags_filter:
        filters = TodoFilters(
            status=status_filter, priority=priority_filter, tags=tags_filter
        )

    sort = TodoSort(sort_by=sort_by, sort_order=sort_order)

    return todo_service.list_todos(filters=filters, sort=sort)


@router.get(
    "/todos/{todo_id}",
    response_model=TodoResponse,
    summary="Get Todo",
    description="Get a specific todo by ID",
)
async def get_todo(
    todo_id: int,
    todo_service: TodoService = Depends(get_todo_service),
) -> TodoResponse:
    """Get a specific todo by ID.

    Args:
        todo_id: Todo ID
        todo_service: Todo service instance

    Returns:
        Todo response

    Raises:
        HTTPException: If todo not found
    """
    logger.debug("Getting todo ID: %s", todo_id)

    try:
        return todo_service.get_todo(todo_id)
    except TodoNotFoundError as e:
        logger.warning("Todo not found: %s", todo_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        ) from e


@router.patch(
    "/todos/{todo_id}",
    response_model=TodoResponse,
    summary="Update Todo",
    description="Update an existing todo item (partial update allowed)",
)
async def update_todo(
    todo_id: int,
    update_data: TodoUpdate,
    todo_service: TodoService = Depends(get_todo_service),
) -> TodoResponse:
    """Update an existing todo item.

    Args:
        todo_id: Todo ID
        update_data: Update data
        todo_service: Todo service instance

    Returns:
        Updated todo response

    Raises:
        HTTPException: If todo not found or update fails
    """
    logger.info("Updating todo ID: %s", todo_id)

    try:
        return todo_service.update_todo(todo_id, update_data)
    except TodoNotFoundError as e:
        logger.warning("Todo not found for update: %s", todo_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        ) from e
    except Exception as e:
        logger.exception("Failed to update todo: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update todo",
        ) from e


@router.delete(
    "/todos/{todo_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Todo",
    description="Delete a todo item (soft delete)",
)
async def delete_todo(
    todo_id: int,
    todo_service: TodoService = Depends(get_todo_service),
) -> None:
    """Delete a todo item (soft delete).

    Args:
        todo_id: Todo ID
        todo_service: Todo service instance

    Raises:
        HTTPException: If todo not found
    """
    logger.info("Deleting todo ID: %s", todo_id)

    try:
        todo_service.delete_todo(todo_id)
    except TodoNotFoundError as e:
        logger.warning("Todo not found for deletion: %s", todo_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        ) from e
    except Exception as e:
        logger.exception("Failed to delete todo: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete todo",
        ) from e
