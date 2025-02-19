"""Tools for interacting with Node-RED."""
import json
from datetime import datetime
import aiohttp
from typing import Dict, Any, Optional
from .base_tool import Tool, ToolConfig, ToolResponse


class NodeREDStatusTool:
    """Tool for checking Node-RED status."""
    
    def __init__(self, config: ToolConfig):
        self.config = config
        self.endpoint = "http://127.0.0.1:1880"
    
    async def validate_dependencies(self) -> bool:
        """Check if Node-RED is available."""
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
        """Check Node-RED status.
        
        Args:
            query: Query to execute
            parameters: Not used
            
        Returns:
            Status response as JSON string
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.endpoint}/list/temperatures") as resp:
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


class TemperatureTool:
    """Tool for getting temperature data."""
    
    def __init__(self, config: ToolConfig):
        self.config = config
        self.endpoint = "http://127.0.0.1:1880"
    
    async def validate_dependencies(self) -> bool:
        """Check if Node-RED and temperature endpoints are available."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.endpoint}/query/temperature?date=2025-02-04") as resp:
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
            # D'abord récupérer la liste des températures pour avoir la date la plus récente
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.endpoint}/list/temperatures") as resp:
                    if resp.status != 200:
                        response: ToolResponse = {
                            "success": False,
                            "data": None,
                            "error": f"Failed to get temperature list: {resp.status}"
                        }
                        return json.dumps(response)
                    
                    data = await resp.json()
                    if not data.get("measurements"):
                        response: ToolResponse = {
                            "success": False,
                            "data": None,
                            "error": "No temperature measurements available"
                        }
                        return json.dumps(response)
                    
                    # Récupérer la date la plus récente
                    latest_date = data["measurements"][0]["date"]
                    
                    # Si une date est spécifiée, la nettoyer
                    target_date = latest_date
                    if parameters and "date" in parameters:
                        cleaned_date = parameters["date"].replace("date='", "").replace("'", "")
                        try:
                            # Vérifier si la date est valide
                            datetime.strptime(cleaned_date, "%Y-%m-%d")
                            target_date = cleaned_date
                        except ValueError:
                            # Si la date n'est pas valide, utiliser la plus récente
                            pass
                    
                    # Faire la requête avec la date cible
                    async with session.get(f"{self.endpoint}/query/temperature?date={target_date}") as resp:
                        if resp.status != 200:
                            # Si la date demandée n'existe pas, utiliser la plus récente
                            async with session.get(f"{self.endpoint}/query/temperature?date={latest_date}") as resp2:
                                if resp2.status != 200:
                                    response: ToolResponse = {
                                        "success": False,
                                        "data": None,
                                        "error": f"Node-RED returned status {resp2.status}"
                                    }
                                    return json.dumps(response)
                                
                                data = await resp2.json()
                                response: ToolResponse = {
                                    "success": True,
                                    "data": data,
                                    "error": None
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
