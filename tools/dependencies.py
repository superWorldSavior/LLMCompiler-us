from dataclasses import dataclass
import os
from typing import Dict, Any, Optional
import aiohttp
from dotenv import load_dotenv
import logfire

# Configure logfire
logfire.configure()
logger = logfire.Logfire()

class NodeREDDependencies:
    """Dependencies for Node-RED API."""
    
    def __init__(self, base_url: str = "http://127.0.0.1:1880"):
        """Initialize Node-RED dependencies.
        
        Args:
            base_url: Base URL for Node-RED API
        """
        self.base_url = base_url
    
    async def request(self, endpoint: str, method: str = "GET", params: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Make a request to Node-RED API.
        
        Args:
            endpoint: API endpoint
            method: HTTP method
            params: Query parameters
            
        Returns:
            Response data
            
        Raises:
            Exception: If request fails
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            async with aiohttp.ClientSession() as session:
                logger.info("Starting request to Node-RED", 
                    method=method,
                    url=url,
                    params=params,
                    headers=dict(session.headers)
                )
                
                async with session.request(method, url, params=params) as response:
                    logger.info("Received response from Node-RED",
                        status=response.status,
                        headers=dict(response.headers),
                        content_type=response.content_type,
                        charset=response.charset,
                        content_length=response.content_length
                    )
                    
                    # Log raw response text for debugging
                    raw_text = await response.text()
                    logger.info("Raw response text", text=raw_text)
                    
                    response.raise_for_status()
                    
                    try:
                        result = await response.json()
                        logger.info("Parsed JSON response", 
                            result=result,
                            result_type=type(result).__name__,
                            result_keys=list(result.keys()) if isinstance(result, dict) else None,
                            result_length=len(result) if isinstance(result, (list, dict)) else None
                        )
                        return result
                    except aiohttp.ContentTypeError as e:
                        logger.error("Failed to parse JSON response",
                            error=str(e),
                            content_type=response.content_type,
                            raw_text=raw_text
                        )
                        raise
        except Exception as e:
            logger.error("Node-RED request failed", 
                error=str(e),
                error_type=type(e).__name__
            )
            raise

class TemperatureDependencies:
    """Class to manage temperature dependencies."""
    
    def __init__(self):
        """Initialize with environment variables."""
        load_dotenv()
        self.node_red_api = os.getenv("NODE_RED_API", "http://127.0.0.1:1880")
        self.node_red_api_key = os.getenv("NODE_RED_API_KEY")
        
    async def _get_headers(self) -> Dict[str, str]:
        """Get headers for Node-RED API requests."""
        headers = {"Content-Type": "application/json"}
        if self.node_red_api_key:
            headers["Authorization"] = f"Bearer {self.node_red_api_key}"
        return headers
        
    async def check_node_red_status(self) -> Dict[str, Any]:
        """Check if Node-RED is running and accessible."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.node_red_api}/settings",
                    headers=await self._get_headers()
                ) as response:
                    if response.status == 200:
                        return {
                            "status": "ok",
                            "message": "Node-RED is running and accessible"
                        }
                    return {
                        "status": "error",
                        "message": f"Node-RED returned status code {response.status}"
                    }
        except aiohttp.ClientError as e:
            return {
                "status": "error",
                "message": f"Failed to connect to Node-RED: {str(e)}"
            }

    async def check_sqlite_status(self) -> Dict[str, Any]:
        """Check if SQLite database is accessible."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.node_red_api}/list/temperatures",
                    headers=await self._get_headers()
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "status": "ok",
                            "message": "SQLite database is accessible",
                            "measurements_count": len(result.get("measurements", []))
                        }
                    return {
                        "status": "error",
                        "message": f"SQLite database check failed with status code {response.status}"
                    }
        except aiohttp.ClientError as e:
            return {
                "status": "error",
                "message": f"Failed to check SQLite database: {str(e)}"
            }
            
    async def check_all_dependencies(self) -> Dict[str, Any]:
        """Check all dependencies."""
        return {
            "node_red": await self.check_node_red_status(),
            "sqlite": await self.check_sqlite_status()
        }
