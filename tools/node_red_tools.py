"""Tools for interacting with Node-RED."""
import json
import aiohttp
from typing import Dict, Any, Optional
from .base_tool import Tool, ToolConfig, ToolResponse


class NodeREDStatusTool:
    """Tool for checking Node-RED status."""
    
    def __init__(self, config: ToolConfig):
        self.config = config
        self.endpoint = "http://localhost:1880"
    
    async def validate_dependencies(self) -> bool:
        """Check if Node-RED is available."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.endpoint}/status") as resp:
                    return resp.status == 200
        except Exception:
            return False
    
    async def execute(
        self,
        query: str,
        parameters: Optional[Dict[str, Any]] = None
    ) -> str:
        """Check Node-RED status.
        
        Args:
            query: Query to execute
            parameters: Not used
            
        Returns:
            Status response as JSON string
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.endpoint}/status") as resp:
                    if resp.status != 200:
                        response: ToolResponse = {
                            "success": False,
                            "data": None,
                            "error": f"Node-RED returned status {resp.status}"
                        }
                        return json.dumps(response)
                    
                    data = await resp.json()
                    response: ToolResponse = {
                        "success": True,
                        "data": {
                            "status": "running" if data.get("status") == "ok" else "error",
                            "message": data.get("message", "Node-RED is running")
                        },
                        "error": None
                    }
                    return json.dumps(response)
                    
        except Exception as e:
            response: ToolResponse = {
                "success": False,
                "data": None,
                "error": str(e)
            }
            return json.dumps(response)


class TemperatureTool:
    """Tool for getting temperature data."""
    
    def __init__(self, config: ToolConfig):
        self.config = config
        self.endpoint = "http://localhost:1880"
    
    async def validate_dependencies(self) -> bool:
        """Check if Node-RED and temperature endpoints are available."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.endpoint}/list/temperatures") as resp:
                    return resp.status == 200
        except Exception:
            return False
    
    async def execute(
        self,
        query: str,
        parameters: Optional[Dict[str, Any]] = None
    ) -> str:
        """Get temperature data.
        
        Args:
            query: Query to execute
            parameters: Optional parameters
                - date: Date to get temperature for (YYYY-MM-DD)
                - start_date: Start date for range (YYYY-MM-DD)
                - end_date: End date for range (YYYY-MM-DD)
            
        Returns:
            Temperature data as JSON string
        """
        try:
            async with aiohttp.ClientSession() as session:
                if parameters and parameters.get("date"):
                    url = f"{self.endpoint}/query/temperature?date={parameters['date']}"
                elif parameters and parameters.get("start_date") and parameters.get("end_date"):
                    url = f"{self.endpoint}/query/temperature?start_date={parameters['start_date']}&end_date={parameters['end_date']}"
                else:
                    url = f"{self.endpoint}/list/temperatures"
                
                async with session.get(url) as resp:
                    if resp.status != 200:
                        response: ToolResponse = {
                            "success": False,
                            "data": None,
                            "error": f"Node-RED returned status {resp.status}"
                        }
                        return json.dumps(response)
                    
                    data = await resp.json()
                    response: ToolResponse = {
                        "success": True,
                        "data": data,
                        "error": None
                    }
                    return json.dumps(response)
                    
        except Exception as e:
            response: ToolResponse = {
                "success": False,
                "data": None,
                "error": str(e)
            }
            return json.dumps(response)


# Register tools
Tool.register(NodeREDStatusTool)
Tool.register(TemperatureTool)
