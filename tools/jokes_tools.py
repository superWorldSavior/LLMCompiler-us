"""Tool pour les blagues Chuck Norris."""
from typing import Dict, Any, Optional
import aiohttp
import json
from loguru import logger
from .base_tool import Tool, ToolConfig


# Configure loguru
logger.remove(0)


class ChuckNorrisJokeTool(Tool):
    """Tool pour générer des blagues Chuck Norris."""
    
    def __init__(self, config: ToolConfig):
        """Initialize le tool.
        
        Args:
            config: Configuration du tool
        """
        super().__init__(config)
        # Chuck Norris API is optional, use default if not configured
        self.endpoint = self.get_service_endpoint(
            "chucknorris-api",
            default_endpoint="https://api.chucknorris.io"
        )
    
    async def validate_dependencies(self) -> bool:
        """Vérifie que l'API Chuck Norris est disponible.
        
        Returns:
            True si l'API répond, False sinon
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.endpoint}/jokes/random") as resp:
                    return resp.status == 200
        except:
            return False
    
    async def validate_parameters(self, parameters: Dict[str, Any]) -> bool:
        """Pas de paramètres requis pour les blagues.
        
        Args:
            parameters: Paramètres extraits de la requête
            
        Returns:
            Toujours True car pas de paramètres requis
        """
        return True
    
    async def execute(self, query: str, parameters: Dict[str, Any] = None) -> str:
        """Génère une blague Chuck Norris.
        
        Args:
            query: Requête utilisateur (ignorée)
            parameters: Paramètres (ignorés)
            
        Returns:
            Réponse formatée avec la blague
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.endpoint}/jokes/random") as resp:
                    if resp.status != 200:
                        return json.dumps({
                            "success": False,
                            "message": f"Erreur {resp.status}",
                            "error": "Impossible d'obtenir une blague"
                        })
                        
                    data = await resp.json()
                    joke = data.get("value", "")
                    
                    return json.dumps({
                        "success": True,
                        "message": "Voici une blague Chuck Norris",
                        "joke": joke
                    })
                    
        except Exception as e:
            logger.error(f"Erreur lors de la requête: {str(e)}")
            return json.dumps({
                "success": False,
                "message": "Erreur interne",
                "error": str(e)
            })


Tool.register(ChuckNorrisJokeTool)
