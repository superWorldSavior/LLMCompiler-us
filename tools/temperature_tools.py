"""Tools for temperature data with streaming support."""
import json
from datetime import datetime
from typing import Dict, Any, List, Optional, TypedDict, NotRequired
import aiohttp
from loguru import logger
from .base_tool import Tool, ToolConfig, ToolResponse


class TemperatureData(TypedDict):
    """Single temperature measurement."""
    date: str
    temperature: float
    unit: NotRequired[str]  # Optional, defaults to °C


class TemperatureListResponse(TypedDict):
    """Response containing a list of temperatures."""
    temperatures: List[TemperatureData]


def validate_date(date_str: str) -> bool:
    """Validate date format YYYY-MM-DD."""
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def validate_temperature(temp: float) -> bool:
    """Validate temperature is within reasonable range."""
    return isinstance(temp, (int, float)) and -50 <= temp <= 50


class SingleTemperatureTool:
    """Tool to get temperature for a single date."""
    
    def __init__(self, config: ToolConfig):
        self.config = config
        self.base_url = "http://localhost:1880"
    
    async def validate_dependencies(self) -> bool:
        """Check if Node-RED is available."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/status") as resp:
                    return resp.status == 200
        except Exception:
            return False
    
    async def execute(
        self,
        query: str,
        parameters: Optional[Dict[str, Any]] = None
    ) -> str:
        """Get temperature for a date."""
        if not parameters or "date" not in parameters:
            response: ToolResponse = {
                "success": False,
                "data": None,
                "error": "Date parameter is required"
            }
            return json.dumps(response)
        
        if not validate_date(parameters["date"]):
            response: ToolResponse = {
                "success": False,
                "data": None,
                "error": "Invalid date format. Use YYYY-MM-DD"
            }
            return json.dumps(response)
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/query/temperature",
                    params={"date": parameters["date"]}
                ) as resp:
                    if resp.status != 200:
                        response: ToolResponse = {
                            "success": False,
                            "data": None,
                            "error": f"Node-RED returned status {resp.status}"
                        }
                        return json.dumps(response)
                    
                    data = await resp.json()
                    temp = data.get("temperature")
                    
                    if not validate_temperature(temp):
                        response: ToolResponse = {
                            "success": False,
                            "data": None,
                            "error": "Invalid temperature value from Node-RED"
                        }
                        return json.dumps(response)
                    
                    temp_data: TemperatureData = {
                        "date": parameters["date"],
                        "temperature": temp,
                        "unit": "°C"
                    }
                    
                    response: ToolResponse = {
                        "success": True,
                        "data": temp_data,
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


class ListTemperatureTool:
    """Tool to get temperature for a date range."""
    
    def __init__(self, config: ToolConfig):
        self.config = config
        self.base_url = "http://localhost:1880"
    
    async def validate_dependencies(self) -> bool:
        """Check if Node-RED is available."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/status") as resp:
                    return resp.status == 200
        except Exception:
            return False
    
    async def execute(
        self,
        query: str,
        parameters: Optional[Dict[str, Any]] = None
    ) -> str:
        """Get temperatures for a date range."""
        if not parameters or "start_date" not in parameters or "end_date" not in parameters:
            response: ToolResponse = {
                "success": False,
                "data": None,
                "error": "start_date and end_date parameters are required"
            }
            return json.dumps(response)
        
        if not validate_date(parameters["start_date"]) or not validate_date(parameters["end_date"]):
            response: ToolResponse = {
                "success": False,
                "data": None,
                "error": "Invalid date format. Use YYYY-MM-DD"
            }
            return json.dumps(response)
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/list/temperatures",
                    params=parameters
                ) as resp:
                    if resp.status != 200:
                        response: ToolResponse = {
                            "success": False,
                            "data": None,
                            "error": f"Node-RED returned status {resp.status}"
                        }
                        return json.dumps(response)
                    
                    data = await resp.json()
                    temps: List[TemperatureData] = []
                    
                    for t in data.get("temperatures", []):
                        temp = t.get("temperature")
                        if not validate_temperature(temp):
                            response: ToolResponse = {
                                "success": False,
                                "data": None,
                                "error": f"Invalid temperature value from Node-RED: {temp}"
                            }
                            return json.dumps(response)
                            
                        temps.append({
                            "date": t["date"],
                            "temperature": temp,
                            "unit": "°C"
                        })
                    
                    temp_list: TemperatureListResponse = {
                        "temperatures": temps
                    }
                    
                    response: ToolResponse = {
                        "success": True,
                        "data": temp_list,
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
Tool.register(SingleTemperatureTool)
Tool.register(ListTemperatureTool)
