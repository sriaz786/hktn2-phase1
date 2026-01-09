"""MCP tool definitions and registration."""

import json
import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class ToolRegistry:
    """Registry for MCP tools."""

    def __init__(self) -> None:
        """Initialize tool registry."""
        self.tools: Dict[str, Dict[str, Any]] = {}
        logger.info("MCP tool registry initialized")

    def register_tool(self, name: str, definition: Dict[str, Any]) -> None:
        """Register an MCP tool.

        Args:
            name: Tool name
            definition: Tool definition with schema
        """
        self.tools[name] = definition
        logger.debug("Registered MCP tool: %s", name)

    def get_tool(self, name: str) -> Dict[str, Any]:
        """Get a tool by name.

        Args:
            name: Tool name

        Returns:
            Tool definition or None if not found
        """
        return self.tools.get(name)

    def list_tools(self) -> List[Dict[str, Any]]:
        """List all registered tools.

        Returns:
            List of tool definitions
        """
        return list(self.tools.values())

    def get_tools_schema(self) -> Dict[str, Any]:
        """Get schema of all tools for MCP protocol.

        Returns:
            MCP tools schema
        """
        return {"tools": self.list_tools()}


# Global registry instance
registry = ToolRegistry()


def initialize_tools() -> None:
    """Initialize all MCP tools."""
    logger.info("Initializing MCP tools...")

    # Define todo-related tools
    tools = [
        {
            "name": "create_todo",
            "description": "Create a new todo item",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "minLength": 1,
                        "maxLength": 200,
                        "description": "Todo title (required)",
                    },
                    "description": {
                        "type": "string",
                        "maxLength": 2000,
                        "description": "Todo description",
                    },
                    "due_date": {
                        "type": "string",
                        "format": "date-time",
                        "description": "Due date for the todo (ISO 8601 format)",
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["low", "medium", "high", "urgent"],
                        "default": "medium",
                        "description": "Todo priority level",
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of tags for the todo",
                    },
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
                        "description": "Filter todos by status",
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["low", "medium", "high", "urgent"],
                        "description": "Filter todos by priority",
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Filter todos by tags",
                    },
                },
            },
        },
        {
            "name": "update_todo",
            "description": "Update an existing todo item (partial update)",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "id": {
                        "type": "integer",
                        "description": "Todo ID to update (required)",
                    },
                    "title": {
                        "type": "string",
                        "minLength": 1,
                        "maxLength": 200,
                        "description": "New title for the todo",
                    },
                    "description": {
                        "type": "string",
                        "maxLength": 2000,
                        "description": "New description for the todo",
                    },
                    "status": {
                        "type": "string",
                        "enum": ["pending", "in_progress", "completed", "cancelled"],
                        "description": "New status for the todo",
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["low", "medium", "high", "urgent"],
                        "description": "New priority for the todo",
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "New tags for the todo",
                    },
                },
                "required": ["id"],
            },
        },
        {
            "name": "delete_todo",
            "description": "Delete a todo item (soft delete)",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "id": {
                        "type": "integer",
                        "description": "Todo ID to delete (required)",
                    },
                },
                "required": ["id"],
            },
        },
    ]

    # Register all tools
    for tool in tools:
        registry.register_tool(tool["name"], tool)

    logger.info("Registered %d MCP tools", len(tools))


def validate_tool_params(tool_name: str, params: Dict[str, Any]) -> bool:
    """Validate tool parameters against schema.

    Args:
        tool_name: Tool name
        params: Tool parameters

    Returns:
        True if valid, False otherwise
    """
    tool = registry.get_tool(tool_name)
    if not tool:
        logger.warning("Tool not found for validation: %s", tool_name)
        return False

    schema = tool.get("inputSchema", {})
    required = schema.get("required", [])

    # Check required fields
    for field in required:
        if field not in params:
            logger.warning("Missing required field '%s' for tool %s", field, tool_name)
            return False

    return True


def format_mcp_response(data: Any, error: bool = False) -> Dict[str, Any]:
    """Format response for MCP protocol.

    Args:
        data: Response data
        error: Whether this is an error response

    Returns:
        Formatted MCP response
    """
    if error:
        return {"status": "error", "error": {"message": str(data)}}
    return {"status": "success", "data": data}


# Initialize tools on module load
initialize_tools()
