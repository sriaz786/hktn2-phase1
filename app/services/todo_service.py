"""Todo service for business logic."""

import logging
from typing import List, Optional

from sqlmodel import Session

from app.models.schemas import (
    TodoCreate,
    TodoFilters,
    TodoListResponse,
    TodoResponse,
    TodoSort,
    TodoUpdate,
)
from app.models.todo import Priority, Status, Todo
from app.repository.todo_repository import TodoRepository

logger = logging.getLogger(__name__)


class TodoNotFoundError(Exception):
    """Exception raised when todo is not found."""

    pass


class TodoService:
    """Service for todo business logic."""

    def __init__(self, repository: TodoRepository) -> None:
        """Initialize todo service.

        Args:
            repository: Todo repository instance
        """
        self.repository = repository

    def create_todo(self, todo_data: TodoCreate) -> TodoResponse:
        """Create a new todo item.

        Args:
            todo_data: Todo creation data

        Returns:
            Created todo response

        Raises:
            Exception: If database operation fails
        """
        logger.info("Creating todo: %s", todo_data.title)

        # Apply defaults
        priority = todo_data.priority or Priority.MEDIUM

        # Create entity
        todo = Todo(
            title=todo_data.title,
            description=todo_data.description,
            due_date=todo_data.due_date,
            priority=priority,
            status=Status.PENDING,
            tags=todo_data.tags or [],
        )

        # Save to database
        created_todo = self.repository.create(todo)

        logger.info("Todo created successfully: ID=%s", created_todo.id)
        return self._to_response(created_todo)

    def get_todo(self, todo_id: int) -> TodoResponse:
        """Get a todo by ID.

        Args:
            todo_id: Todo ID

        Returns:
            Todo response

        Raises:
            TodoNotFoundError: If todo not found
        """
        logger.debug("Getting todo ID: %s", todo_id)

        todo = self.repository.get_by_id(todo_id)
        if not todo:
            logger.warning("Todo not found: %s", todo_id)
            raise TodoNotFoundError(f"Todo with id {todo_id} not found")

        return self._to_response(todo)

    def list_todos(
        self, filters: Optional[TodoFilters] = None, sort: Optional[TodoSort] = None
    ) -> TodoListResponse:
        """List todos with optional filtering and sorting.

        Args:
            filters: Filter criteria
            sort: Sort criteria

        Returns:
            Todo list response with metadata
        """
        logger.debug("Listing todos with filters=%s, sort=%s", filters, sort)

        todos = self.repository.list_all(filters=filters, sort=sort)
        total = self.repository.count_total(filters)

        return TodoListResponse(
            data=[self._to_response(todo) for todo in todos],
            metadata={"total": total, "page": 1, "page_size": len(todos)},
        )

    def update_todo(self, todo_id: int, update_data: TodoUpdate) -> TodoResponse:
        """Update a todo item.

        Args:
            todo_id: Todo ID
            update_data: Update data

        Returns:
            Updated todo response

        Raises:
            TodoNotFoundError: If todo not found
            Exception: If database operation fails
        """
        logger.info("Updating todo ID: %s", todo_id)

        # Convert update data to dict, excluding None values
        update_dict = update_data.model_dump(exclude_none=True)

        if not update_dict:
            logger.debug("No update data provided for todo %s", todo_id)
            # Return existing todo without changes
            return self.get_todo(todo_id)

        updated_todo = self.repository.update(todo_id, update_dict)

        if not updated_todo:
            logger.warning("Todo not found for update: %s", todo_id)
            raise TodoNotFoundError(f"Todo with id {todo_id} not found")

        logger.info("Todo updated successfully: ID=%s", todo_id)
        return self._to_response(updated_todo)

    def delete_todo(self, todo_id: int) -> None:
        """Delete a todo item (soft delete).

        Args:
            todo_id: Todo ID

        Raises:
            TodoNotFoundError: If todo not found
        """
        logger.info("Deleting todo ID: %s", todo_id)

        success = self.repository.delete(todo_id)

        if not success:
            logger.warning("Todo not found for deletion: %s", todo_id)
            raise TodoNotFoundError(f"Todo with id {todo_id} not found")

        logger.info("Todo deleted successfully: ID=%s", todo_id)

    def _to_response(self, todo: Todo) -> TodoResponse:
        """Convert Todo entity to response.

        Args:
            todo: Todo entity

        Returns:
            TodoResponse
        """
        return TodoResponse.model_validate(todo)
