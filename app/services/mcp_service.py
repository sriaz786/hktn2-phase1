"""MCP service for server initialization and tool handling."""

import json
import logging
from typing import Any, Dict, List, Optional

from app.models.schemas import (
    TodoCreate,
    TodoResponse,
    TodoUpdate,
)
from app.models.todo import Priority, Status
from app.services.todo_service import TodoService

logger = logging.getLogger(__name__)


class MCPServiceError(Exception):
    """Exception raised when MCP service fails."""

    pass


class MCPService:
    """Service for MCP server and tool handling."""

    def __init__(self, todo_service: TodoService) -> None:
        """Initialize MCP service.

        Args:
            todo_service: Todo service instance
        """
        self.todo_service = todo_service
        self.tools = self._define_tools()
        logger.info("MCP service initialized with %d tools", len(self.tools))

    def get_tools_list(self) -> List[Dict[str, Any]]:
        """Get list of available MCP tools.

        Returns:
            List of tool definitions
        """
        return self.tools

    async def handle_tool_call(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle an MCP tool call.

        Args:
            tool_name: Name of the tool to call
            params: Tool parameters

        Returns:
            Tool execution result

        Raises:
            MCPServiceError: If tool not found or execution fails
        """
        logger.info("Handling MCP tool call: %s", tool_name)

        tool_handlers = {
            "create_todo": self.create_todo_tool,
            "list_todos": self.list_todos_tool,
            "update_todo": self.update_todo_tool,
            "delete_todo": self.delete_todo_tool,
        }

        handler = tool_handlers.get(tool_name)
        if not handler:
            logger.error("Unknown MCP tool: %s", tool_name)
            raise MCPServiceError(f"Unknown tool: {tool_name}")

        try:
            result = await handler(params)
            logger.debug("Tool %s executed successfully", tool_name)
            return result
        except Exception as e:
            logger.exception("Tool %s execution failed: %s", tool_name, e)
            return self._format_error(str(e))

    async def create_todo_tool(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a todo via MCP tool.

        Args:
            params: Tool parameters (title, description, due_date, priority, tags)

        Returns:
            Created todo response
        """
        logger.debug("MCP create_todo with params: %s", params)

        # Validate required fields
        if "title" not in params:
            return self._format_error("Missing required field: title")

        # Create todo
        todo_data = TodoCreate(
            title=params["title"],
            description=params.get("description"),
            due_date=params.get("due_date"),
            priority=Priority(params.get("priority", "medium")),
            tags=params.get("tags", []),
        )

        todo = self.todo_service.create_todo(todo_data)
        return self._format_success(todo.model_dump())

    async def list_todos_tool(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List todos via MCP tool.

        Args:
            params: Tool parameters (status, priority)

        Returns:
            List of todos
        """
        logger.debug("MCP list_todos with params: %s", params)

        from app.models.schemas import TodoFilters

        # Build filters
        filters = TodoFilters(
            status=Status(params["status"]) if "status" in params else None,
            priority=Priority(params["priority"]) if "priority" in params else None,
            tags=params.get("tags"),
        )

        # Get todos
        result = self.todo_service.list_todos(filters=filters)

        return self._format_success(
            {"todos": [t.model_dump() for t in result.data], "total": len(result.data)}
        )

    async def update_todo_tool(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Update a todo via MCP tool.

        Args:
            params: Tool parameters (id, title, description, status, priority, tags)

        Returns:
            Updated todo response
        """
        logger.debug("MCP update_todo with params: %s", params)

        # Validate required fields
        if "id" not in params:
            return self._format_error("Missing required field: id")

        # Build update data
        update_dict = {}
        for key in ["title", "description", "status", "priority", "tags"]:
            if key in params:
                if key == "status":
                    update_dict[key] = Status(params[key])
                elif key == "priority":
                    update_dict[key] = Priority(params[key])
                else:
                    update_dict[key] = params[key]

        update_data = TodoUpdate(**update_dict)

        todo = self.todo_service.update_todo(params["id"], update_data)
        return self._format_success(todo.model_dump())

    async def delete_todo_tool(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Delete a todo via MCP tool.

        Args:
            params: Tool parameters (id)

        Returns:
            Deletion confirmation
        """
        logger.debug("MCP delete_todo with params: %s", params)

        # Validate required fields
        if "id" not in params:
            return self._format_error("Missing required field: id")

        self.todo_service.delete_todo(params["id"])

        return self._format_success({"deleted": True, "id": params["id"]})

    def _define_tools(self) -> List[Dict[str, Any]]:
        """Define available MCP tools.

        Returns:
            List of tool definitions with schemas
        """
        return [
            {
                "name": "create_todo",
                "description": "Create a new todo item",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string", "description": "Todo title (required)"},
                        "description": {"type": "string", "description": "Todo description"},
                        "due_date": {"type": "string", "format": "date-time", "description": "Due date"},
                        "priority": {
                            "type": "string",
                            "enum": ["low", "medium", "high", "urgent"],
                            "default": "medium",
                            "description": "Todo priority",
                        },
                        "tags": {"type": "array", "items": {"type": "string"}, "description": "Todo tags"},
                    },
                    "required": ["title"],
                },
            },
            {
                "name": "list_todos",
                "description": "List all todo items with optional filters",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "status": {
                            "type": "string",
                            "enum": ["pending", "in_progress", "completed", "cancelled"],
                            "description": "Filter by status",
                        },
                        "priority": {
                            "type": "string",
                            "enum": ["low", "medium", "high", "urgent"],
                            "description": "Filter by priority",
                        },
                        "tags": {"type": "array", "items": {"type": "string"}, "description": "Filter by tags"},
                    },
                },
            },
            {
                "name": "update_todo",
                "description": "Update an existing todo item",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer", "description": "Todo ID (required)"},
                        "title": {"type": "string", "description": "New title"},
                        "description": {"type": "string", "description": "New description"},
                        "status": {
                            "type": "string",
                            "enum": ["pending", "in_progress", "completed", "cancelled"],
                            "description": "New status",
                        },
                        "priority": {
                            "type": "string",
                            "enum": ["low", "medium", "high", "urgent"],
                            "description": "New priority",
                        },
                        "tags": {"type": "array", "items": {"type": "string"}, "description": "New tags"},
                    },
                    "required": ["id"],
                },
            },
            {
                "name": "delete_todo",
                "description": "Delete a todo item",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer", "description": "Todo ID (required)"},
                    },
                    "required": ["id"],
                },
            },
        ]

    def _format_success(self, data: Any) -> Dict[str, Any]:
        """Format successful tool result.

        Args:
            data: Result data

        Returns:
            Formatted success response
        """
        return {"status": "success", "data": data}

    def _format_error(self, message: str) -> Dict[str, Any]:
        """Format error response.

        Args:
            message: Error message

        Returns:
            Formatted error response
        """
        return {"status": "error", "error": {"message": message}}
