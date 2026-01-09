"""Unit tests for MCP service."""

from unittest.mock import AsyncMock, Mock

import pytest

from app.models.todo import Priority, Status
from app.services.mcp_service import MCPService, MCPServiceError
from app.services.todo_service import TodoService


# Test fixtures
@pytest.fixture
def mock_todo_service():
    """Create mock todo service."""
    service = Mock(spec=TodoService)
    return service


@pytest.fixture
def mcp_service(mock_todo_service):
    """Create MCP service instance."""
    return MCPService(mock_todo_service)


# ==================== MCP Service Tests ====================


class TestMCPService:
    """Tests for MCPService."""

    def test_initialization(self, mcp_service):
        """Test MCP service initialization."""
        assert mcp_service.todo_service is not None
        assert len(mcp_service.tools) == 4  # Should have 4 tools

    def test_get_tools_list(self, mcp_service):
        """Test getting list of tools."""
        tools = mcp_service.get_tools_list()

        assert isinstance(tools, list)
        assert len(tools) == 4

        tool_names = [t["name"] for t in tools]
        assert "create_todo" in tool_names
        assert "list_todos" in tool_names
        assert "update_todo" in tool_names
        assert "delete_todo" in tool_names

    @pytest.mark.asyncio
    async def test_handle_tool_call_unknown_tool(self, mcp_service):
        """Test handling unknown tool."""
        result = await mcp_service.handle_tool_call("unknown_tool", {})

        assert result["status"] == "error"
        assert "Unknown tool" in result["error"]["message"]

    @pytest.mark.asyncio
    async def test_create_todo_tool_success(self, mcp_service, mock_todo_service):
        """Test successful todo creation via MCP tool."""
        mock_todo_service.create_todo = Mock(
            return_value=Mock(id=1, title="Test Todo", model_dump=lambda: {"id": 1, "title": "Test Todo"})
        )

        params = {"title": "Test Todo", "priority": "high"}

        result = await mcp_service.handle_tool_call("create_todo", params)

        assert result["status"] == "success"
        assert "data" in result
        assert result["data"]["id"] == 1
        mock_todo_service.create_todo.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_todo_tool_missing_title(self, mcp_service):
        """Test todo creation tool with missing title."""
        params = {"description": "No title"}

        result = await mcp_service.handle_tool_call("create_todo", params)

        assert result["status"] == "error"
        assert "Missing required field: title" in result["error"]["message"]

    @pytest.mark.asyncio
    async def test_create_todo_tool_with_all_fields(self, mcp_service, mock_todo_service):
        """Test todo creation with all fields."""
        mock_todo_service.create_todo = Mock(
            return_value=Mock(
                id=1,
                title="Complete Task",
                description="Task Description",
                priority=Priority.HIGH,
                tags=["work", "urgent"],
                model_dump=lambda: {
                    "id": 1,
                    "title": "Complete Task",
                    "description": "Task Description",
                    "priority": "high",
                    "tags": ["work", "urgent"],
                },
            )
        )

        params = {
            "title": "Complete Task",
            "description": "Task Description",
            "priority": "high",
            "tags": ["work", "urgent"],
        }

        result = await mcp_service.handle_tool_call("create_todo", params)

        assert result["status"] == "success"
        assert result["data"]["title"] == "Complete Task"
        assert result["data"]["description"] == "Task Description"
        assert result["data"]["priority"] == "high"
        assert result["data"]["tags"] == ["work", "urgent"]

    @pytest.mark.asyncio
    async def test_list_todos_tool_success(self, mcp_service, mock_todo_service):
        """Test successful todo listing via MCP tool."""
        mock_todo_service.list_todos = Mock(
            return_value=Mock(
                data=[
                    Mock(id=1, title="First", model_dump=lambda: {"id": 1, "title": "First"}),
                    Mock(id=2, title="Second", model_dump=lambda: {"id": 2, "title": "Second"}),
                ],
            )
        )

        result = await mcp_service.handle_tool_call("list_todos", {})

        assert result["status"] == "success"
        assert "data" in result
        assert "todos" in result["data"]
        assert len(result["data"]["todos"]) == 2

    @pytest.mark.asyncio
    async def test_list_todos_with_filters(self, mcp_service, mock_todo_service):
        """Test listing todos with filters."""
        mock_todo_service.list_todos = Mock(
            return_value=Mock(
                data=[
                    Mock(id=1, title="Pending", model_dump=lambda: {"id": 1, "title": "Pending"}),
                ],
            )
        )

        params = {"status": "pending", "priority": "high"}

        result = await mcp_service.handle_tool_call("list_todos", params)

        assert result["status"] == "success"
        mock_todo_service.list_todos.assert_called_once()
        # Verify filters were applied
        call_args = mock_todo_service.list_todos.call_args
        assert call_args is not None

    @pytest.mark.asyncio
    async def test_update_todo_tool_success(self, mcp_service, mock_todo_service):
        """Test successful todo update via MCP tool."""
        mock_todo_service.update_todo = Mock(
            return_value=Mock(
                id=1,
                title="Updated Title",
                status=Status.IN_PROGRESS,
                model_dump=lambda: {"id": 1, "title": "Updated Title", "status": "in_progress"},
            )
        )

        params = {"id": 1, "status": "in_progress", "priority": "urgent"}

        result = await mcp_service.handle_tool_call("update_todo", params)

        assert result["status"] == "success"
        assert result["data"]["id"] == 1
        assert result["data"]["title"] == "Updated Title"
        mock_todo_service.update_todo.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_todo_tool_missing_id(self, mcp_service):
        """Test todo update tool with missing id."""
        params = {"status": "in_progress"}

        result = await mcp_service.handle_tool_call("update_todo", params)

        assert result["status"] == "error"
        assert "Missing required field: id" in result["error"]["message"]

    @pytest.mark.asyncio
    async def test_delete_todo_tool_success(self, mcp_service, mock_todo_service):
        """Test successful todo deletion via MCP tool."""
        mock_todo_service.delete_todo = Mock()

        params = {"id": 1}

        result = await mcp_service.handle_tool_call("delete_todo", params)

        assert result["status"] == "success"
        assert result["data"]["deleted"] is True
        assert result["data"]["id"] == 1
        mock_todo_service.delete_todo.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_delete_todo_tool_missing_id(self, mcp_service):
        """Test todo deletion tool with missing id."""
        params = {}

        result = await mcp_service.handle_tool_call("delete_todo", params)

        assert result["status"] == "error"
        assert "Missing required field: id" in result["error"]["message"]

    def test_tool_schemas_have_required_fields(self, mcp_service):
        """Test that all tools have required schema fields."""
        tools = mcp_service.get_tools_list()

        for tool in tools:
            assert "name" in tool
            assert "description" in tool
            assert "inputSchema" in tool
            assert "type" in tool["inputSchema"]
            assert "properties" in tool["inputSchema"]

    def test_create_todo_tool_schema(self, mcp_service):
        """Test create_todo tool schema."""
        create_tool = next((t for t in mcp_service.tools if t["name"] == "create_todo"), None)

        assert create_tool is not None
        assert "title" in create_tool["inputSchema"]["properties"]
        assert "required" in create_tool["inputSchema"]
        assert "title" in create_tool["inputSchema"]["required"]
        assert "description" not in create_tool["inputSchema"]["required"]

    def test_update_todo_tool_schema(self, mcp_service):
        """Test update_todo tool schema."""
        update_tool = next((t for t in mcp_service.tools if t["name"] == "update_todo"), None)

        assert update_tool is not None
        assert "id" in update_tool["inputSchema"]["properties"]
        assert "id" in update_tool["inputSchema"]["required"]
        assert "title" not in update_tool["inputSchema"]["required"]
        assert "status" not in update_tool["inputSchema"]["required"]

    def test_delete_todo_tool_schema(self, mcp_service):
        """Test delete_todo tool schema."""
        delete_tool = next((t for t in mcp_service.tools if t["name"] == "delete_todo"), None)

        assert delete_tool is not None
        assert "id" in delete_tool["inputSchema"]["properties"]
        assert "id" in delete_tool["inputSchema"]["required"]
        assert len(delete_tool["inputSchema"]["required"]) == 1

    @pytest.mark.asyncio
    async def test_format_success(self, mcp_service):
        """Test success response formatting."""
        data = {"id": 1, "title": "Test"}
        result = mcp_service._format_success(data)

        assert result["status"] == "success"
        assert result["data"] == data

    @pytest.mark.asyncio
    async def test_format_error(self, mcp_service):
        """Test error response formatting."""
        result = mcp_service._format_error("Test error message")

        assert result["status"] == "error"
        assert result["error"]["message"] == "Test error message"

    @pytest.mark.asyncio
    async def test_tool_execution_error(self, mcp_service, mock_todo_service):
        """Test tool execution error handling."""
        mock_todo_service.create_todo = Mock(side_effect=Exception("Database error"))

        params = {"title": "Test Todo"}

        result = await mcp_service.handle_tool_call("create_todo", params)

        # Should return error response
        assert result["status"] == "error"
