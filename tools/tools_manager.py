"""Tools manager."""
from typing import Dict, Any, List, Optional
from loguru import logger
from .base_tool import Tool, ToolConfig

logger = logger


class ToolsManager:
    """Manager for tools."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the tools manager.
        
        Args:
            config_path: Path to YAML config file
        """
        self.tools: Dict[str, Tool] = {}
        if config_path:
            self._load_config(config_path)
    
    def _load_config(self, config_path: str) -> None:
        """Load tool configurations from YAML file."""
        logger.info("Loading tools from", config_path=config_path)
        
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
            
        for tool_config in config.get("tools", []):
            # Convert YAML to TypedDict
            config_dict: ToolConfig = {
                "name": tool_config["name"],
                "description": tool_config["description"],
                "category": tool_config["category"],
                "enabled": tool_config.get("enabled", True),
                "required_parameters": [
                    {
                        "name": param["name"],
                        "description": param["description"],
                        "required": param.get("required", True)
                    }
                    for param in tool_config.get("required_parameters", [])
                ],
                "tool_dependencies": [
                    {"tool": dep["tool"]}
                    for dep in tool_config.get("depends", [])
                ]
            }
            
            # Get tool class from registry
            try:
                tool_cls = Tool.get(tool_config["name"])
                tool = tool_cls(config=config_dict)
                self.tools[tool_config["name"]] = tool
                logger.info("Loaded tool", name=tool_config["name"])
            except ValueError as e:
                logger.error("Failed to load tool", 
                    name=tool_config["name"],
                    error=str(e)
                )
    
    def get_tool(self, name: str) -> Tool:
        """Get a tool by name.
        
        Args:
            name: Name of the tool
            
        Returns:
            Tool instance
        """
        if name not in self.tools:
            raise ValueError(f"Tool {name} not found")
        return self.tools[name]
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """List all available tools.
        
        Returns:
            List of tool metadata
        """
        return [
            {
                "name": tool.config["name"],
                "description": tool.config["description"],
                "category": tool.config["category"],
                "enabled": tool.config["enabled"]
            }
            for tool in self.tools.values()
        ]


# Export a singleton instance
tools_manager = ToolsManager()
