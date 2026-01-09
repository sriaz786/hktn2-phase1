"""Unit tests for Todo repository and service."""

import pytest
from datetime import datetime
from sqlmodel import Session, create_engine, SQLModel
from sqlmodel.pool import StaticPool

from app.models.schemas import (
    TodoCreate,
    TodoFilters,
    TodoSort,
    TodoUpdate,
)
from app.models.todo import Priority, Status, Todo
from app.repository.todo_repository import TodoRepository
from app.services.todo_service import TodoNotFoundError, TodoService


# Test fixtures
@pytest.fixture
def test_engine():
    """Create test database engine."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    return engine


@pytest.fixture
def test_session(test_engine):
    """Create test database session."""
    with Session(test_engine) as session:
        yield session
        session.rollback()


@pytest.fixture
def todo_repository(test_session):
    """Create todo repository fixture."""
    return TodoRepository(test_session)


@pytest.fixture
def todo_service(todo_repository):
    """Create todo service fixture."""
    return TodoService(todo_repository)


@pytest.fixture
def sample_todo():
    """Create sample todo fixture."""
    return Todo(
        title="Test Todo",
        description="Test Description",
        priority=Priority.HIGH,
        status=Status.PENDING,
        tags=["test"],
    )


# ==================== Todo Repository Tests ====================


class TestTodoRepository:
    """Tests for TodoRepository."""

    def test_create_todo(self, todo_repository, sample_todo):
        """Test creating a todo."""
        result = todo_repository.create(sample_todo)

        assert result.id is not None
        assert result.title == "Test Todo"
        assert result.description == "Test Description"
        assert result.priority == Priority.HIGH
        assert result.status == Status.PENDING
        assert result.tags == ["test"]
        assert result.is_deleted is False

    def test_get_todo_by_id(self, todo_repository, sample_todo):
        """Test getting a todo by ID."""
        created = todo_repository.create(sample_todo)
        found = todo_repository.get_by_id(created.id)

        assert found is not None
        assert found.id == created.id
        assert found.title == created.title

    def test_get_todo_by_id_not_found(self, todo_repository):
        """Test getting a non-existent todo."""
        result = todo_repository.get_by_id(999)
        assert result is None

    def test_get_deleted_todo(self, todo_repository, sample_todo):
        """Test that deleted todos are not returned."""
        created = todo_repository.create(sample_todo)
        todo_repository.delete(created.id)

        result = todo_repository.get_by_id(created.id)
        assert result is None

    def test_list_all_todos(self, todo_repository, sample_todo):
        """Test listing all todos."""
        todo_repository.create(sample_todo)
        todo_repository.create(
            Todo(title="Second Todo", priority=Priority.LOW, status=Status.PENDING)
        )

        results = todo_repository.list_all()

        assert len(results) == 2
        assert all(isinstance(t, Todo) for t in results)

    def test_list_todos_with_status_filter(self, todo_repository, sample_todo):
        """Test filtering todos by status."""
        todo_repository.create(sample_todo)
        todo_repository.create(
            Todo(title="Completed Todo", status=Status.COMPLETED, priority=Priority.MEDIUM)
        )

        results = todo_repository.list_all(filters=TodoFilters(status=Status.PENDING))

        assert len(results) == 1
        assert results[0].status == Status.PENDING

    def test_list_todos_with_priority_filter(self, todo_repository, sample_todo):
        """Test filtering todos by priority."""
        todo_repository.create(sample_todo)
        todo_repository.create(
            Todo(title="Low Priority Todo", priority=Priority.LOW, status=Status.PENDING)
        )

        results = todo_repository.list_all(filters=TodoFilters(priority=Priority.HIGH))

        assert len(results) == 1
        assert results[0].priority == Priority.HIGH

    def test_list_todos_with_sorting(self, todo_repository):
        """Test sorting todos."""
        todo1 = Todo(title="First", priority=Priority.HIGH, status=Status.PENDING)
        todo2 = Todo(title="Second", priority=Priority.LOW, status=Status.PENDING)
        todo_repository.create(todo1)
        todo_repository.create(todo2)

        sort = TodoSort(sort_by="priority", sort_order="asc")
        results = todo_repository.list_all(sort=sort)

        assert len(results) == 2
        assert results[0].priority == Priority.LOW
        assert results[1].priority == Priority.HIGH

    def test_update_todo(self, todo_repository, sample_todo):
        """Test updating a todo."""
        created = todo_repository.create(sample_todo)

        updated = todo_repository.update(
            created.id,
            {
                "title": "Updated Title",
                "status": Status.IN_PROGRESS,
                "priority": Priority.URGENT,
            },
        )

        assert updated.title == "Updated Title"
        assert updated.status == Status.IN_PROGRESS
        assert updated.priority == Priority.URGENT
        assert updated.modified_at is not None

    def test_update_todo_not_found(self, todo_repository):
        """Test updating a non-existent todo."""
        result = todo_repository.update(999, {"title": "Updated"})
        assert result is None

    def test_delete_todo(self, todo_repository, sample_todo):
        """Test deleting a todo (soft delete)."""
        created = todo_repository.create(sample_todo)

        success = todo_repository.delete(created.id)

        assert success is True

        # Check soft delete
        deleted = todo_repository.get_by_id(created.id)
        assert deleted is None

    def test_delete_todo_not_found(self, todo_repository):
        """Test deleting a non-existent todo."""
        success = todo_repository.delete(999)
        assert success is False

    def test_count_total(self, todo_repository, sample_todo):
        """Test counting total todos."""
        todo_repository.create(sample_todo)
        todo_repository.create(Todo(title="Second Todo", status=Status.PENDING))

        total = todo_repository.count_total()
        assert total == 2


# ==================== Todo Service Tests ====================


class TestTodoService:
    """Tests for TodoService."""

    def test_create_todo(self, todo_service):
        """Test creating a todo via service."""
        todo_data = TodoCreate(
            title="Service Test Todo",
            description="Service Test Description",
            priority=Priority.HIGH,
        )

        result = todo_service.create_todo(todo_data)

        assert result.id is not None
        assert result.title == "Service Test Todo"
        assert result.description == "Service Test Description"
        assert result.priority == Priority.HIGH
        assert result.status == Status.PENDING  # Default status

    def test_create_todo_with_defaults(self, todo_service):
        """Test creating a todo with default values."""
        todo_data = TodoCreate(title="Minimal Todo")

        result = todo_service.create_todo(todo_data)

        assert result.priority == Priority.MEDIUM  # Default priority
        assert result.status == Status.PENDING  # Default status
        assert result.tags == []  # Default tags

    def test_get_todo(self, todo_service):
        """Test getting a todo via service."""
        todo_data = TodoCreate(title="Get Test Todo")
        created = todo_service.create_todo(todo_data)

        result = todo_service.get_todo(created.id)

        assert result.id == created.id
        assert result.title == "Get Test Todo"

    def test_get_todo_not_found(self, todo_service):
        """Test getting a non-existent todo."""
        with pytest.raises(TodoNotFoundError) as exc_info:
            todo_service.get_todo(999)

        assert "Todo with id 999 not found" in str(exc_info.value)

    def test_list_todos(self, todo_service):
        """Test listing todos via service."""
        todo_service.create_todo(TodoCreate(title="First"))
        todo_service.create_todo(TodoCreate(title="Second"))

        result = todo_service.list_todos()

        assert len(result.data) == 2
        assert result.metadata["total"] == 2

    def test_list_todos_with_filters(self, todo_service):
        """Test listing todos with filters via service."""
        todo_service.create_todo(TodoCreate(title="Pending", status=Status.PENDING))
        todo_service.create_todo(TodoCreate(title="Completed", status=Status.COMPLETED))

        result = todo_service.list_todos(filters=TodoFilters(status=Status.PENDING))

        assert len(result.data) == 1
        assert result.data[0].status == Status.PENDING

    def test_update_todo(self, todo_service):
        """Test updating a todo via service."""
        created = todo_service.create_todo(TodoCreate(title="Original Title"))

        update_data = TodoUpdate(title="Updated Title", status=Status.IN_PROGRESS)
        result = todo_service.update_todo(created.id, update_data)

        assert result.title == "Updated Title"
        assert result.status == Status.IN_PROGRESS

    def test_update_todo_empty(self, todo_service):
        """Test updating a todo with empty data."""
        created = todo_service.create_todo(TodoCreate(title="Test"))

        update_data = TodoUpdate()
        result = todo_service.update_todo(created.id, update_data)

        # Should return existing todo without changes
        assert result.title == "Test"

    def test_update_todo_not_found(self, todo_service):
        """Test updating a non-existent todo."""
        update_data = TodoUpdate(title="Updated")

        with pytest.raises(TodoNotFoundError) as exc_info:
            todo_service.update_todo(999, update_data)

        assert "Todo with id 999 not found" in str(exc_info.value)

    def test_delete_todo(self, todo_service):
        """Test deleting a todo via service."""
        created = todo_service.create_todo(TodoCreate(title="To Delete"))

        todo_service.delete_todo(created.id)

        # Verify deletion
        with pytest.raises(TodoNotFoundError):
            todo_service.get_todo(created.id)

    def test_delete_todo_not_found(self, todo_service):
        """Test deleting a non-existent todo."""
        with pytest.raises(TodoNotFoundError) as exc_info:
            todo_service.delete_todo(999)

        assert "Todo with id 999 not found" in str(exc_info.value)
