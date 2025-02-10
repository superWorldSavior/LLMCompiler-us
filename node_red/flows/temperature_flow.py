from typing import Dict, List, Any
import os
from .base_flow import NodeRedFlow

class TemperatureFlow(NodeRedFlow):
    """Flow for temperature measurements API."""
    
    @property
    def name(self) -> str:
        return "Temperature Measurements API"
        
    @property
    def description(self) -> str:
        return "API endpoint for querying temperature measurements"
    
    def generate_nodes(self) -> List[Dict[str, Any]]:
        """Generate nodes for temperature measurement flow."""
        # Get absolute path to database
        current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        db_path = os.path.join(current_dir, 'db', 'measurements.db')
        
        # Print the path for debugging
        print(f"Using database path: {db_path}")
        
        # Generate unique IDs for nodes
        http_in_id = f"{self.tab_id}_http_in"
        validate_id = f"{self.tab_id}_validate"
        sqlite_id = f"{self.tab_id}_sqlite"
        format_id = f"{self.tab_id}_format"
        http_out_id = f"{self.tab_id}_http_out"
        db_config_id = f"{self.tab_id}_db_config"
        debug1_id = f"{self.tab_id}_debug1"
        debug2_id = f"{self.tab_id}_debug2"
        debug3_id = f"{self.tab_id}_debug3"
        
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
                "name": "Temperature Query Endpoint",
                "url": "/query/temperature",
                "method": "get",
                "upload": False,
                "swaggerDoc": "",
                "x": 120,
                "y": 100,
                "wires": [[validate_id, debug1_id]]
            },
            
            # Debug 1 - Input
            {
                "id": debug1_id,
                "type": "debug",
                "z": self.tab_id,
                "name": "Debug Input",
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
            
            # Validate Date Function Node
            {
                "id": validate_id,
                "type": "function",
                "z": self.tab_id,
                "name": "Validate Date",
                "func": """
                if (!msg.req.query.date) {
                    msg.statusCode = 400;
                    msg.payload = {
                        error: "Date parameter is required",
                        status: "invalid_request",
                        code: 400
                    };
                    return [null, msg];
                }

                const dateRegex = /^\\d{4}-\\d{2}-\\d{2}$/;
                if (!dateRegex.test(msg.req.query.date)) {
                    msg.statusCode = 400;
                    msg.payload = {
                        error: "Invalid date format. Please use YYYY-MM-DD",
                        status: "invalid_format",
                        code: 400
                    };
                    return [null, msg];
                }

                msg.params = {
                    $date: msg.req.query.date
                };
                return [msg, null];
                """,
                "outputs": 2,
                "noerr": 0,
                "initialize": "",
                "finalize": "",
                "libs": [],
                "x": 320,
                "y": 100,
                "wires": [[sqlite_id, debug2_id], [http_out_id]]
            },
            
            # Debug 2 - Before SQL
            {
                "id": debug2_id,
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
                "x": 320,
                "y": 160,
                "wires": []
            },
            
            # SQLite Query Node
            {
                "id": sqlite_id,
                "type": "sqlite",
                "z": self.tab_id,
                "name": "Query Measurements",
                "mydb": db_config_id,
                "sqlquery": "prepared",
                "sql": "SELECT * FROM measurements WHERE date = $date",
                "params": [],
                "x": 520,
                "y": 100,
                "wires": [[format_id, debug3_id]]
            },
            
            # Debug 3 - After SQL
            {
                "id": debug3_id,
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
                "x": 520,
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
                        error: `No measurement found for date ${msg.params.$date}`,
                        status: "not_found",
                        code: 404
                    };
                    return msg;
                }

                const measurement = msg.payload[0];
                msg.payload = {
                    date: measurement.date,
                    temperature: measurement.temperature,
                    humidity: measurement.humidity,
                    metadata: {
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
