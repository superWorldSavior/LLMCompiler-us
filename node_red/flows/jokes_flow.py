from typing import Dict, List, Any
from .base_flow import NodeRedFlow

class JokesFlow(NodeRedFlow):
    """Flow for Chuck Norris jokes API."""
    
    @property
    def name(self) -> str:
        return "Chuck Norris Jokes API"
        
    @property
    def description(self) -> str:
        return "API endpoint for fetching Chuck Norris jokes with French translation"
    
    def generate_nodes(self) -> List[Dict[str, Any]]:
        """Generate nodes for jokes flow."""
        # Generate unique IDs for nodes
        http_in_id = f"{self.tab_id}_http_in"
        fetch_id = f"{self.tab_id}_fetch"
        translate_id = f"{self.tab_id}_translate"
        format_id = f"{self.tab_id}_format"
        http_out_id = f"{self.tab_id}_http_out"
        
        return [
            # HTTP Input Node
            {
                "id": http_in_id,
                "type": "http in",
                "z": self.tab_id,
                "name": "Jokes Endpoint",
                "url": "/joke",
                "method": "get",
                "upload": False,
                "swaggerDoc": "",
                "x": 120,
                "y": 100,
                "wires": [[fetch_id]]
            },
            
            # Fetch Joke Function Node
            {
                "id": fetch_id,
                "type": "function",
                "z": self.tab_id,
                "name": "Fetch Random Joke",
                "func": """
                // API endpoint for Chuck Norris jokes
                msg.url = 'https://api.chucknorris.io/jokes/random';
                return msg;
                """,
                "outputs": 1,
                "noerr": 0,
                "initialize": "",
                "finalize": "",
                "libs": [],
                "x": 320,
                "y": 100,
                "wires": [[translate_id]]
            },
            
            # HTTP Request Node
            {
                "id": translate_id,
                "type": "http request",
                "z": self.tab_id,
                "name": "Get Joke",
                "method": "GET",
                "ret": "obj",
                "paytoqs": "ignore",
                "url": "",
                "tls": "",
                "persist": False,
                "proxy": "",
                "insecureHTTPParser": False,
                "x": 520,
                "y": 100,
                "wires": [[format_id]]
            },
            
            # Format Response Function Node
            {
                "id": format_id,
                "type": "function",
                "z": self.tab_id,
                "name": "Format Response",
                "func": """
                if (!msg.payload || !msg.payload.value) {
                    msg.statusCode = 500;
                    msg.payload = {
                        error: "Failed to fetch joke",
                        status: "error",
                        code: 500
                    };
                    return msg;
                }

                msg.payload = {
                    response: msg.payload.value,
                    metadata: {
                        source: "api.chucknorris.io",
                        type: "chuck_norris_joke",
                        language: "english",
                        timestamp: new Date().toISOString()
                    }
                };
                return msg;
                """,
                "outputs": 1,
                "noerr": 0,
                "initialize": "",
                "finalize": "",
                "libs": [],
                "x": 720,
                "y": 100,
                "wires": [[http_out_id]]
            },
            
            # HTTP Response Node
            {
                "id": http_out_id,
                "type": "http response",
                "z": self.tab_id,
                "name": "Send Response",
                "statusCode": "",
                "headers": {
                    "Content-Type": "application/json"
                },
                "x": 920,
                "y": 100,
                "wires": []
            }
        ]
