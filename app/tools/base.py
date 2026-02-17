"""Base tool classes for agentic system"""

from __future__ import annotations

import inspect
from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class ToolResult:
    """Result from tool execution"""
    success: bool
    data: Any
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class BaseTool:
    """Base class for all agent tools"""

    name: str = ""
    description: str = ""

    async def execute(self, **kwargs) -> ToolResult:
        """Execute the tool with given parameters"""
        raise NotImplementedError(f"{self.__class__.__name__} must implement execute()")

    def to_gemini_tool(self) -> Dict[str, Any]:
        """Convert to Gemini function calling format"""
        sig = inspect.signature(self.execute)
        parameters = {}
        required_params = []

        for param_name, param in sig.parameters.items():
            if param_name in ("self", "kwargs"):
                continue

            # Get type annotation
            param_type = param.annotation
            json_type = self._python_to_json_type(param_type)

            # Get description from docstring if available
            param_desc = f"Parameter {param_name}"

            parameters[param_name] = {
                "type": json_type,
                "description": param_desc
            }

            # Check if required (no default value)
            if param.default == inspect.Parameter.empty:
                required_params.append(param_name)

        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": parameters,
                "required": required_params
            }
        }

    def _python_to_json_type(self, python_type) -> str:
        """Convert Python type to JSON schema type"""
        type_mapping = {
            str: "string",
            int: "integer",
            float: "number",
            bool: "boolean",
            list: "array",
            dict: "object"
        }

        # Handle Optional types
        if hasattr(python_type, "__origin__"):
            if python_type.__origin__ is list:
                return "array"
            elif python_type.__origin__ is dict:
                return "object"

        # Get the actual type if Optional
        if hasattr(python_type, "__args__"):
            for arg in python_type.__args__:
                if arg is not type(None):
                    python_type = arg
                    break

        return type_mapping.get(python_type, "string")
