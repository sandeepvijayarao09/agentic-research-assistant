"""Tool Registry - Central hub for function calling and tool management"""

import json
import logging
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class ToolSchema(BaseModel):
    """JSON Schema definition for tool parameters"""
    name: str
    description: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    required: List[str] = Field(default_factory=list)


class Tool:
    """Represents a callable tool with schema"""

    def __init__(
        self,
        name: str,
        func: Callable,
        description: str,
        parameters: Dict[str, Any],
        required: List[str],
    ):
        self.name = name
        self.func = func
        self.description = description
        self.parameters = parameters
        self.required = required

    def to_schema(self) -> Dict[str, Any]:
        """Convert tool to OpenAI-compatible schema"""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": self.parameters,
                    "required": self.required,
                },
            },
        }

    async def execute(self, **kwargs) -> str:
        """Execute the tool with error handling"""
        try:
            logger.info(f"Executing tool: {self.name} with args: {kwargs}")

            # Check for async functions
            if hasattr(self.func, "__await__"):
                result = await self.func(**kwargs)
            else:
                result = self.func(**kwargs)

            logger.info(f"Tool {self.name} completed successfully")
            return str(result)
        except Exception as e:
            error_msg = f"Tool execution error in {self.name}: {str(e)}"
            logger.error(error_msg)
            return f"Error: {error_msg}"


class ToolRegistry:
    """Central registry for all available tools"""

    def __init__(self):
        self.tools: Dict[str, Tool] = {}
        self._init_builtin_tools()

    def _init_builtin_tools(self):
        """Initialize built-in tools"""
        # Calculator tool
        self.register(
            name="calculator",
            func=self._calculator,
            description="Perform mathematical calculations",
            parameters={
                "operation": {
                    "type": "string",
                    "description": "Mathematical operation: add, subtract, multiply, divide, power",
                },
                "x": {
                    "type": "number",
                    "description": "First number",
                },
                "y": {
                    "type": "number",
                    "description": "Second number",
                },
            },
            required=["operation", "x", "y"],
        )

        # DateTime tool
        self.register(
            name="get_current_time",
            func=self._get_current_time,
            description="Get current date and time",
            parameters={},
            required=[],
        )

        # Memory recall tool
        self.register(
            name="recall_memory",
            func=self._recall_memory,
            description="Recall information from long-term memory",
            parameters={
                "query": {
                    "type": "string",
                    "description": "Query to search memory",
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of results",
                },
            },
            required=["query"],
        )

    def register(
        self,
        name: str,
        func: Callable,
        description: str,
        parameters: Dict[str, Any],
        required: List[str],
    ) -> None:
        """Register a new tool"""
        tool = Tool(name, func, description, parameters, required)
        self.tools[name] = tool
        logger.info(f"Registered tool: {name}")

    def get_tool(self, name: str) -> Optional[Tool]:
        """Get a tool by name"""
        return self.tools.get(name)

    def get_schemas(self) -> List[Dict[str, Any]]:
        """Get all tool schemas for LLM function calling"""
        return [tool.to_schema() for tool in self.tools.values()]

    async def execute_tool(self, tool_name: str, **kwargs) -> str:
        """Execute a tool by name"""
        tool = self.get_tool(tool_name)
        if not tool:
            return f"Error: Tool '{tool_name}' not found"

        return await tool.execute(**kwargs)

    def list_tools(self) -> List[str]:
        """List all available tool names"""
        return list(self.tools.keys())

    # Built-in tool implementations

    @staticmethod
    def _calculator(operation: str, x: float, y: float) -> float:
        """Perform mathematical operations"""
        operations = {
            "add": lambda a, b: a + b,
            "subtract": lambda a, b: a - b,
            "multiply": lambda a, b: a * b,
            "divide": lambda a, b: a / b if b != 0 else float("inf"),
            "power": lambda a, b: a ** b,
        }

        if operation not in operations:
            raise ValueError(f"Unknown operation: {operation}")

        return operations[operation](x, y)

    @staticmethod
    def _get_current_time() -> str:
        """Get current date and time"""
        return datetime.now().isoformat()

    @staticmethod
    def _recall_memory(query: str, limit: int = 5) -> str:
        """Placeholder for memory recall - will be implemented with actual memory system"""
        return f"Memory recall not yet configured for query: {query}"
