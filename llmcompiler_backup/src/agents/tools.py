from typing import List, Optional

from langchain_core.callbacks import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from langchain_core.tools import BaseTool

from src.tools.base import Tool, tool


class InvalidTool(BaseTool):
    """Tool that is run when invalid tool name is encountered by agent."""

    name: str = "invalid_tool"
    description: str = "Called when tool name is invalid. Suggests valid tool names."

    def _run(
        self,
        requested_tool_name: str,
        available_tool_names: List[str],
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool."""
        available_tool_names_str = ", ".join([tool for tool in available_tool_names])
        return (
            f"{requested_tool_name} is not a valid tool, "
            f"try one of [{available_tool_names_str}]."
        )

    async def _arun(
        self,
        requested_tool_name: str,
        available_tool_names: List[str],
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool asynchronously."""
        return self._run(requested_tool_name, available_tool_names, run_manager)


__all__ = ["InvalidTool", "BaseTool", "tool", "Tool"]
