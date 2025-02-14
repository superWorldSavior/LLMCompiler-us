"""Base classes and types for tools."""
from typing import Dict, Any, List, Optional, TypedDict, Protocol, runtime_checkable, ClassVar


class RequiredParameter(TypedDict):
    """Represents a required parameter for a tool."""
    name: str
    description: str
    required: bool


class ToolDependency(TypedDict):
    """Represents a dependency on another tool."""
    tool: str


class ToolConfig(TypedDict):
    """Configuration for a tool."""
    name: str
    description: str
    category: str
    enabled: bool
    required_parameters: List[RequiredParameter]
    tool_dependencies: List[ToolDependency]


class ToolMetadata(TypedDict):
    """Metadata about a tool."""
    name: str
    description: str
    version: str
    category: str


class ToolResponse(TypedDict):
    """Response from a tool execution."""
    success: bool
    data: Optional[Dict[str, Any]]
    error: Optional[str]


class ToolImplementation(TypedDict):
    """Implementation details of a tool."""
    metadata: ToolMetadata
    config: ToolConfig


@runtime_checkable
class Tool(Protocol):
    """Protocol for all tools."""
    _registry: ClassVar[Dict[str, type["Tool"]]] = {}
    config: ToolConfig
    
    async def validate_dependencies(self) -> bool:
        """Validate that all dependencies are available.
        
        Returns:
            True if all dependencies are available
        """
        ...
    
    async def execute(
        self,
        query: str,
        parameters: Optional[Dict[str, Any]] = None
    ) -> str:
        """Execute the tool.
        
        Args:
            query: Query to execute
            parameters: Optional parameters
            
        Returns:
            Tool response as JSON string
        """
        ...
        
    @classmethod
    def register(cls, tool_cls: type["Tool"]) -> type["Tool"]:
        """Register a tool class."""
        cls._registry[tool_cls.__name__] = tool_cls
        return tool_cls
    
    @classmethod
    def get(cls, name: str) -> type["Tool"]:
        """Get a registered tool class."""
        if name not in cls._registry:
            raise ValueError(f"Tool {name} not found")
        return cls._registry[name]
