"""Todo repository for database operations."""

import logging
from datetime import datetime
from typing import List, Optional

from sqlmodel import Session, col, select

from app.models.schemas import TodoFilters, TodoSort
from app.models.todo import Priority, Status, Todo

logger = logging.getLogger(__name__)


class TodoRepository:
    """Repository for Todo database operations."""

    def __init__(self, session: Session) -> None:
        """Initialize repository with database session.

        Args:
            session: SQLAlchemy session
        """
        self.session = session

    def create(self, todo_data: Todo) -> Todo:
        """Create a new todo item.

        Args:
            todo_data: Todo entity to create

        Returns:
            Created todo entity

        Raises:
            Exception: If database operation fails
        """
        logger.info("Creating todo: %s", todo_data.title)
        self.session.add(todo_data)
        self.session.commit()
        self.session.refresh(todo_data)
        logger.debug("Todo created with ID: %s", todo_data.id)
        return todo_data

    def get_by_id(self, todo_id: int) -> Optional[Todo]:
        """Get a todo by ID.

        Args:
            todo_id: Todo ID

        Returns:
            Todo entity or None if not found
        """
        logger.debug("Fetching todo by ID: %s", todo_id)
        statement = select(Todo).where(Todo.id == todo_id, Todo.is_deleted == False)
        return self.session.exec(statement).first()

    def list_all(self, filters: Optional[TodoFilters] = None, sort: Optional[TodoSort] = None) -> List[Todo]:
        """List all todos with optional filtering and sorting.

        Args:
            filters: Filter criteria
            sort: Sort criteria

        Returns:
            List of todo entities
        """
        logger.debug("Listing todos with filters: %s, sort: %s", filters, sort)
        statement = select(Todo).where(Todo.is_deleted == False)

        # Apply filters
        if filters:
            if filters.status:
                statement = statement.where(Todo.status == filters.status)
            if filters.priority:
                statement = statement.where(Todo.priority == filters.priority)
            if filters.tags:
                # Filter by any matching tag
                for tag in filters.tags:
                    statement = statement.where(Todo.tags.contains(tag))

        # Apply sorting
        if sort:
            sort_column = getattr(Todo, sort.sort_by, Todo.created_at)
            if sort.sort_order == "asc":
                statement = statement.order_by(sort_column)
            else:
                statement = statement.order_by(col(sort_column).desc())

        return self.session.exec(statement).all()

    def update(self, todo_id: int, update_data: dict) -> Optional[Todo]:
        """Update a todo item.

        Args:
            todo_id: Todo ID
            update_data: Dictionary of fields to update

        Returns:
            Updated todo entity or None if not found

        Raises:
            Exception: If database operation fails
        """
        logger.info("Updating todo ID: %s with data: %s", todo_id, update_data)
        todo = self.get_by_id(todo_id)
        if not todo:
            logger.warning("Todo not found for update: %s", todo_id)
            return None

        # Update fields
        for key, value in update_data.items():
            if hasattr(todo, key) and key not in ["id", "created_at"]:
                setattr(todo, key, value)

        # Update modified timestamp
        todo.modified_at = datetime.utcnow()

        self.session.commit()
        self.session.refresh(todo)
        logger.debug("Todo updated: %s", todo_id)
        return todo

    def delete(self, todo_id: int) -> bool:
        """Delete a todo item (soft delete).

        Args:
            todo_id: Todo ID

        Returns:
            True if deleted, False if not found

        Raises:
            Exception: If database operation fails
        """
        logger.info("Deleting todo ID: %s", todo_id)
        todo = self.get_by_id(todo_id)
        if not todo:
            logger.warning("Todo not found for deletion: %s", todo_id)
            return False

        todo.is_deleted = True
        todo.modified_at = datetime.utcnow()

        self.session.commit()
        logger.debug("Todo soft deleted: %s", todo_id)
        return True

    def count_total(self, filters: Optional[TodoFilters] = None) -> int:
        """Count total todos with optional filtering.

        Args:
            filters: Filter criteria

        Returns:
            Count of todos matching filters
        """
        statement = select(Todo).where(Todo.is_deleted == False)

        if filters:
            if filters.status:
                statement = statement.where(Todo.status == filters.status)
            if filters.priority:
                statement = statement.where(Todo.priority == filters.priority)

        return len(self.session.exec(statement).all())
