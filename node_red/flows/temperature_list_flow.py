from typing import Dict, List, Any
import os
from .base_flow import NodeRedFlow

class TemperatureListFlow(NodeRedFlow):
    """Flow for listing all available temperature measurements."""
    
    @property
    def name(self) -> str:
        return "Temperature List API"
        
    @property
    def description(self) -> str:
        return "API endpoint for listing all available temperature measurements"
    
    def generate_nodes(self) -> List[Dict[str, Any]]:
        """Generate nodes for temperature list flow."""
        # Get absolute path to database
        current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        db_path = os.path.join(current_dir, 'db', 'measurements.db')
        
        # Print the path for debugging
        print(f"Using database path: {db_path}")
        
        # Generate unique IDs for nodes
        http_in_id = f"{self.tab_id}_http_in"
        sqlite_id = f"{self.tab_id}_sqlite"
        format_id = f"{self.tab_id}_format"
        http_out_id = f"{self.tab_id}_http_out"
        db_config_id = f"{self.tab_id}_db_config"
        debug1_id = f"{self.tab_id}_debug1"
        debug2_id = f"{self.tab_id}_debug2"
        
        return [
            # SQLite DB Configuration
            {
                "id": db_config_id,
                "type": "sqlitedb",
                "z": "",  # Global config node
                "name": "measurements_db",
                "db": db_path,
                "mode": "RWC"
            },
            
            # HTTP Input Node
            {
                "id": http_in_id,
                "type": "http in",
                "z": self.tab_id,
                "name": "Temperature List Endpoint",
                "url": "/list/temperatures",
                "method": "get",
                "upload": False,
                "swaggerDoc": "",
                "x": 120,
                "y": 100,
                "wires": [[sqlite_id, debug1_id]]
            },
            
            # Debug 1 - Before SQL
            {
                "id": debug1_id,
                "type": "debug",
                "z": self.tab_id,
                "name": "Debug Before SQL",
                "active": True,
                "tosidebar": True,
                "console": True,
                "complete": "true",
                "targetType": "full",
                "statusVal": "",
                "statusType": "auto",
                "x": 120,
                "y": 160,
                "wires": []
            },
            
            # SQLite Query Node
            {
                "id": sqlite_id,
                "type": "sqlite",
                "z": self.tab_id,
                "name": "List Measurements",
                "mydb": db_config_id,
                "sqlquery": "fixed",
                "sql": "SELECT date, temperature, humidity FROM measurements ORDER BY date DESC",
                "params": [],
                "x": 320,
                "y": 100,
                "wires": [[format_id, debug2_id]]
            },
            
            # Debug 2 - After SQL
            {
                "id": debug2_id,
                "type": "debug",
                "z": self.tab_id,
                "name": "Debug After SQL",
                "active": True,
                "tosidebar": True,
                "console": True,
                "complete": "true",
                "targetType": "full",
                "statusVal": "",
                "statusType": "auto",
                "x": 320,
                "y": 160,
                "wires": []
            },
            
            # Format Response Function Node
            {
                "id": format_id,
                "type": "function",
                "z": self.tab_id,
                "name": "Format Response",
                "func": """
                if (!msg.payload || msg.payload.length === 0) {
                    msg.statusCode = 404;
                    msg.payload = {
                        error: "No measurements found",
                        status: "not_found",
                        code: 404
                    };
                    return msg;
                }

                msg.payload = {
                    measurements: msg.payload.map(m => ({
                        date: m.date,
                        temperature: m.temperature,
                        humidity: m.humidity
                    })),
                    metadata: {
                        count: msg.payload.length,
                        measurement_type: "environmental",
                        temperature_unit: "celsius",
                        humidity_unit: "percentage",
                        data_source: "local_sqlite_db",
                        measurement_location: "office_environment",
                        accuracy: "high",
                        calibration_date: "2024-01-01"
                    },
                    query_timestamp: new Date().toISOString()
                };
                return msg;
                """,
                "outputs": 1,
                "noerr": 0,
                "initialize": "",
                "finalize": "",
                "libs": [],
                "x": 520,
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
                "x": 720,
                "y": 100,
                "wires": []
            }
        ]
