"""Base tool definition."""
from abc import ABC, abstractmethod
from typing import Dict, Any
from pydantic import BaseModel, Field
from pydantic_ai import Agent

class BaseTool(BaseModel, ABC):
    """Base class for all tools."""
    
    name: str = Field(..., description="The name of the tool")
    description: str = Field(..., description="A description of what the tool does")
    
    @abstractmethod
    def _create_agent(self) -> Agent:
        """Create and configure the Pydantic AI agent for this tool.
        
        Returns:
            Configured Pydantic AI agent
        """
        pass
    
    @abstractmethod
    async def execute(self, query: str) -> str:
        """Execute the tool with the given query.
        
        Args:
            query: The input query for the tool
            
        Returns:
            The tool's response as a string
        """
        pass
