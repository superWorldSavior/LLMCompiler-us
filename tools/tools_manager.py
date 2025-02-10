"""Tools manager for loading and managing tools."""
from typing import Dict, Type, List
import importlib
import os
import inspect
import logfire
from .base_tool import BaseTool
from .jokes import jokes_tool
from .temperature_query import temperature_tool

# Configure logfire for project "test"
logfire.configure()
logger = logfire.Logfire()

class ToolsManager:
    """Manager for loading and managing tools."""
    
    def __init__(self):
        """Initialize the tools manager."""
        logger.info("Initializing tools manager...")
        self._tools: Dict[str, BaseTool] = {
            jokes_tool.name: jokes_tool,
            temperature_tool.name: temperature_tool
        }
        logger.info(f"Loaded {len(self._tools)} tools: {list(self._tools.keys())}")
    
    async def execute_tool(self, name: str, query: str) -> str:
        """Execute a tool by name.
        
        Args:
            name: Name of the tool to execute
            query: Query to pass to the tool
            
        Returns:
            Tool's response
            
        Raises:
            KeyError: If tool not found
        """
        logger.info(f"Executing tool: {name}")
        if name not in self._tools:
            raise KeyError(f"Tool {name} not found")
        return await self._tools[name].execute(query)
    
    def get_available_tools(self) -> Dict[str, str]:
        """Get available tools.
        
        Returns:
            Dictionary of tool names and descriptions
        """
        logger.info("Getting available tools...")
        return {
            name: tool.description
            for name, tool in self._tools.items()
        }

# Export a singleton instance
tools_manager = ToolsManager()
