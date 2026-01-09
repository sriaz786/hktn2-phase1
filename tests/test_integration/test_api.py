"""Integration tests for API endpoints."""

from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient

from app.main import app
from app.models.schemas import TodoCreate


# Test fixtures
@pytest.fixture
def test_client():
    """Create test client for FastAPI app."""
    with patch("app.services.ai_service.AsyncOpenAI"):
        client = TestClient(app)
        yield client


@pytest.fixture
def async_test_client():
    """Create async test client."""
    with patch("app.services.ai_service.AsyncOpenAI"):
        return AsyncClient(app=app, base_url="http://test")


# ==================== Root and Health Tests ====================


class TestRootEndpoint:
    """Tests for root endpoint."""

    def test_root_endpoint(self, test_client):
        """Test root endpoint returns API info."""
        response = test_client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Evolution of Todo API"
        assert data["version"] == "1.0.0"
        assert data["status"] == "Phase 1"
        assert "/docs" in data


class TestHealthCheck:
    """Tests for health check endpoint."""

    def test_health_check(self, test_client):
        """Test health check endpoint."""
        response = test_client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "message" in data


# ==================== Todo CRUD Tests ====================


class TestTodoCRUD:
    """Integration tests for todo CRUD operations."""

    def test_create_todo(self, test_client):
        """Test creating a todo via API."""
        todo_data = {"title": "Test Todo", "description": "Test Description", "priority": "high"}

        response = test_client.post("/api/v1/todos", json=todo_data)

        assert response.status_code == 201
        data = response.json()["data"]
        assert data["title"] == "Test Todo"
        assert data["description"] == "Test Description"
        assert data["priority"] == "high"
        assert data["status"] == "pending"
        assert "id" in data
        assert "created_at" in data

    def test_create_todo_minimal(self, test_client):
        """Test creating a todo with only required fields."""
        todo_data = {"title": "Minimal Todo"}

        response = test_client.post("/api/v1/todos", json=todo_data)

        assert response.status_code == 201
        data = response.json()["data"]
        assert data["title"] == "Minimal Todo"
        assert data["priority"] == "medium"  # Default
        assert data["status"] == "pending"  # Default

    def test_create_todo_invalid(self, test_client):
        """Test creating a todo with invalid data."""
        todo_data = {}  # Missing required title

        response = test_client.post("/api/v1/todos", json=todo_data)

        assert response.status_code == 400
        assert "error" in response.json()

    def test_get_todo(self, test_client):
        """Test getting a single todo."""
        # First create a todo
        create_response = test_client.post(
            "/api/v1/todos", json={"title": "Get Test Todo"}
        )
        todo_id = create_response.json()["data"]["id"]

        # Then get it
        response = test_client.get(f"/api/v1/todos/{todo_id}")

        assert response.status_code == 200
        data = response.json()["data"]
        assert data["id"] == todo_id
        assert data["title"] == "Get Test Todo"

    def test_get_todo_not_found(self, test_client):
        """Test getting a non-existent todo."""
        response = test_client.get("/api/v1/todos/999")

        assert response.status_code == 404
        assert "not found" in response.json()["error"]["message"].lower()

    def test_list_todos(self, test_client):
        """Test listing all todos."""
        # Create multiple todos
        test_client.post("/api/v1/todos", json={"title": "First"})
        test_client.post("/api/v1/todos", json={"title": "Second"})

        response = test_client.get("/api/v1/todos")

        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "metadata" in data
        assert len(data["data"]) >= 2

    def test_list_todos_with_status_filter(self, test_client):
        """Test listing todos filtered by status."""
        # Create todos with different statuses
        test_client.post("/api/v1/todos", json={"title": "Pending", "status": "pending"})
        test_client.post("/api/v1/todos", json={"title": "Completed", "status": "completed"})

        # Filter by status
        response = test_client.get("/api/v1/todos?status=pending")

        assert response.status_code == 200
        data = response.json()["data"]
        assert all(todo["status"] == "pending" for todo in data)

    def test_list_todos_with_priority_filter(self, test_client):
        """Test listing todos filtered by priority."""
        # Create todos with different priorities
        test_client.post("/api/v1/todos", json={"title": "High", "priority": "high"})
        test_client.post("/api/v1/todos", json={"title": "Low", "priority": "low"})

        # Filter by priority
        response = test_client.get("/api/v1/todos?priority=high")

        assert response.status_code == 200
        data = response.json()["data"]
        assert all(todo["priority"] == "high" for todo in data)

    def test_list_todos_with_sorting(self, test_client):
        """Test listing todos with sorting."""
        test_client.post("/api/v1/todos", json={"title": "Low Priority", "priority": "low"})
        test_client.post("/api/v1/todos", json={"title": "High Priority", "priority": "high"})

        # Sort by priority ascending
        response = test_client.get("/api/v1/todos?sort_by=priority&sort_order=asc")

        assert response.status_code == 200
        data = response.json()["data"]
        assert data[0]["priority"] == "low"
        assert data[1]["priority"] == "high"

    def test_update_todo(self, test_client):
        """Test updating a todo."""
        # Create a todo
        create_response = test_client.post(
            "/api/v1/todos", json={"title": "Original Title"}
        )
        todo_id = create_response.json()["data"]["id"]

        # Update it
        update_data = {"title": "Updated Title", "status": "in_progress"}
        response = test_client.patch(f"/api/v1/todos/{todo_id}", json=update_data)

        assert response.status_code == 200
        data = response.json()["data"]
        assert data["title"] == "Updated Title"
        assert data["status"] == "in_progress"

    def test_update_todo_partial(self, test_client):
        """Test partial update of a todo."""
        # Create a todo
        create_response = test_client.post(
            "/api/v1/todos",
            json={"title": "Test", "description": "Original", "priority": "medium"},
        )
        todo_id = create_response.json()["data"]["id"]

        # Update only status
        response = test_client.patch(
            f"/api/v1/todos/{todo_id}", json={"status": "completed"}
        )

        assert response.status_code == 200
        data = response.json()["data"]
        assert data["status"] == "completed"
        assert data["description"] == "Original"  # Unchanged
        assert data["priority"] == "medium"  # Unchanged

    def test_update_todo_not_found(self, test_client):
        """Test updating a non-existent todo."""
        response = test_client.patch("/api/v1/todos/999", json={"title": "Updated"})

        assert response.status_code == 404

    def test_delete_todo(self, test_client):
        """Test deleting a todo (soft delete)."""
        # Create a todo
        create_response = test_client.post(
            "/api/v1/todos", json={"title": "To Delete"}
        )
        todo_id = create_response.json()["data"]["id"]

        # Delete it
        response = test_client.delete(f"/api/v1/todos/{todo_id}")

        assert response.status_code == 204

        # Verify it's deleted
        get_response = test_client.get(f"/api/v1/todos/{todo_id}")
        assert get_response.status_code == 404

    def test_delete_todo_not_found(self, test_client):
        """Test deleting a non-existent todo."""
        response = test_client.delete("/api/v1/todos/999")

        assert response.status_code == 404


# ==================== AI Endpoints Tests ====================


class TestAIEndpoints:
    """Integration tests for AI endpoints."""

    @pytest.mark.asyncio
    async def test_generate_suggestions(self, async_test_client):
        """Test generating AI suggestions."""
        with patch("app.services.ai_service.AsyncOpenAI") as mock_openai:
            mock_client = AsyncMock()
            mock_completion = AsyncMock()
            mock_completion.choices = [
                {
                    "message": {
                        "content": '{"suggestions": [{"title": "Test", "description": "Desc", "priority": "high"}]}'
                    }
                }
            ]
            mock_client.chat.completions.create = AsyncMock(return_value=mock_completion)
            mock_openai.return_value = mock_client

            async with AsyncClient(app=app, base_url="http://test") as client:
                request_data = {"description": "I need to organize my files"}
                response = await client.post("/api/v1/ai/suggest", json=request_data)

                assert response.status_code == 200
                data = response.json()
                assert "suggestions" in data

    @pytest.mark.asyncio
    async def test_prioritize_todos(self, async_test_client):
        """Test AI prioritization."""
        with patch("app.services.ai_service.AsyncOpenAI") as mock_openai:
            mock_client = AsyncMock()
            mock_completion = AsyncMock()
            mock_completion.choices = [
                {
                    "message": {
                        "content": '{"ranked_todos": [{"todo_id": 1, "title": "Task", "recommended_priority": "urgent", "reasoning": "Important"}]}'
                    }
                }
            ]
            mock_client.chat.completions.create = AsyncMock(return_value=mock_completion)
            mock_openai.return_value = mock_client

            async with AsyncClient(app=app, base_url="http://test") as client:
                request_data = {
                    "todos": [
                        {"id": 1, "title": "Task", "due_date": None, "priority": "high"}
                    ]
                }
                response = await client.post("/api/v1/ai/prioritize", json=request_data)

                assert response.status_code == 200
                data = response.json()
                assert "ranked_todos" in data

    @pytest.mark.asyncio
    async def test_breakdown_task(self, async_test_client):
        """Test AI task breakdown."""
        with patch("app.services.ai_service.AsyncOpenAI") as mock_openai:
            mock_client = AsyncMock()
            mock_completion = AsyncMock()
            mock_completion.choices = [
                {
                    "message": {
                        "content": '{"subtasks": [{"title": "First step", "estimated_order": 1, "dependencies": []}]}'
                    }
                }
            ]
            mock_client.chat.completions.create = AsyncMock(return_value=mock_completion)
            mock_openai.return_value = mock_client

            async with AsyncClient(app=app, base_url="http://test") as client:
                request_data = {"task": "Build a REST API"}
                response = await client.post("/api/v1/ai/breakdown", json=request_data)

                assert response.status_code == 200
                data = response.json()
                assert "subtasks" in data


# ==================== Error Handling Tests ====================


class TestErrorHandling:
    """Tests for error handling."""

    def test_validation_error_response(self, test_client):
        """Test validation error response format."""
        response = test_client.post("/api/v1/todos", json={})

        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        assert "code" in data["error"]
        assert "message" in data["error"]
        assert "details" in data["error"]

    def test_404_error_response(self, test_client):
        """Test 404 error response format."""
        response = test_client.get("/api/v1/todos/99999")

        assert response.status_code == 404
        data = response.json()
        assert "error" in data
        assert "not found" in data["error"]["message"].lower()

    def test_method_not_allowed(self, test_client):
        """Test method not allowed error."""
        response = test_client.put("/api/v1/todos")

        assert response.status_code == 405
