import json
import os
import requests
from typing import Dict, List, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Node-RED configuration
NODE_RED_URL = os.getenv("NODE_RED_API", "http://127.0.0.1:1880")
NODE_RED_API_KEY = os.getenv("NODE_RED_API_KEY", "")  # If you have authentication enabled

def generate_node_red_flow() -> List[Dict[str, Any]]:
    """Generate a Node-RED flow for temperature measurements endpoint."""
    
    # Generate unique IDs for nodes
    tab_id = "temperature_measurement_tab"
    http_in_id = "http_temperature_in"
    validate_id = "validate_date"
    sqlite_id = "query_sqlite"
    format_id = "format_response"
    http_out_id = "http_temperature_out"
    
    # Create the flow with tab
    flow = [
        {
            "id": tab_id,
            "type": "tab",
            "label": "Temperature Measurements API",
            "disabled": False,
            "info": "API endpoint for querying temperature measurements"
        },
        # HTTP Input Node
        {
            "id": http_in_id,
            "type": "http in",
            "z": tab_id,
            "name": "Temperature Query Endpoint",
            "url": "/query/temperature",
            "method": "get",
            "upload": False,
            "swaggerDoc": "",
            "x": 120,
            "y": 100,
            "wires": [[validate_id]]
        },
        
        # Validate Date Function Node
        {
            "id": validate_id,
            "type": "function",
            "z": tab_id,
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

            msg.date = msg.req.query.date;
            return [msg, null];
            """,
            "outputs": 2,
            "noerr": 0,
            "initialize": "",
            "finalize": "",
            "libs": [],
            "x": 320,
            "y": 100,
            "wires": [[sqlite_id], [http_out_id]]
        },
        
        # SQLite Query Node
        {
            "id": sqlite_id,
            "type": "sqlite",
            "z": tab_id,
            "name": "Query Measurements",
            "mydb": "C:\\Users\\erpes\\Desktop\\red_node_pimp\\db\\measurements.db",
            "sqlquery": "msg.topic",
            "sql": "SELECT date, temperature, humidity FROM measurements WHERE date = $date",
            "params": [{"type": "str", "value": "msg.date", "param": "date"}],
            "x": 520,
            "y": 100,
            "wires": [[format_id]]
        },
        
        # Format Response Function Node
        {
            "id": format_id,
            "type": "function",
            "z": tab_id,
            "name": "Format Response",
            "func": """
            if (!msg.payload || msg.payload.length === 0) {
                msg.statusCode = 404;
                msg.payload = {
                    error: `No measurement found for date ${msg.date}`,
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
            "z": tab_id,
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
    
    return flow

def deploy_flow_to_node_red(flow: List[Dict[str, Any]]) -> bool:
    """Deploy the flow directly to Node-RED using its API."""
    try:
        # First, check if Node-RED is running
        health_response = requests.get(f"{NODE_RED_URL}/settings")
        if health_response.status_code != 200:
            print("Error: Cannot connect to Node-RED. Make sure it's running.")
            return False

        # Headers for authentication if needed
        headers = {
            "Content-Type": "application/json"
        }
        if NODE_RED_API_KEY:
            headers["Authorization"] = f"Bearer {NODE_RED_API_KEY}"
            
        # Deploy the flows
        deploy_response = requests.post(
            f"{NODE_RED_URL}/flows",
            headers=headers,
            json=flow
        )
        deploy_response.raise_for_status()
        
        print("Flow deployed successfully to Node-RED!")
        print(f"You can access the endpoint at: {NODE_RED_URL}/query/temperature?date=YYYY-MM-DD")
        return True
        
    except requests.exceptions.ConnectionError:
        print("Error: Cannot connect to Node-RED. Make sure it's running.")
        return False
    except Exception as e:
        print(f"Error deploying flow: {str(e)}")
        return False

def save_and_deploy_flow():
    """Save the flow to a JSON file and deploy it to Node-RED."""
    flow = generate_node_red_flow()
    
    # Ensure node_red directory exists
    os.makedirs('node_red', exist_ok=True)
    
    # Save the flow locally as backup
    flow_path = os.path.join('node_red', 'temperature_flow.json')
    with open(flow_path, 'w') as f:
        json.dump(flow, f, indent=2)
    
    print(f"Flow saved locally to {flow_path}")
    
    # Deploy to Node-RED
    if deploy_flow_to_node_red(flow):
        print("\nNext steps:")
        print("1. Make sure you have the SQLite node installed in Node-RED:")
        print("   - Open Node-RED settings")
        print("   - Go to 'Manage palette'")
        print("   - Install 'node-red-node-sqlite'")
        print("\n2. Test the endpoint with:")
        print(f"   {NODE_RED_URL}/query/temperature?date=2024-02-04")
    else:
        print("\nManual import instructions:")
        print("1. Open Node-RED")
        print("2. Click on the menu (≡)")
        print("3. Select 'Import'")
        print("4. Click 'select a file to import'")
        print(f"5. Choose {flow_path}")

if __name__ == '__main__':
    save_and_deploy_flow()
