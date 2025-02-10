import os
import json
import requests
from typing import Dict, List, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Node-RED configuration
NODE_RED_URL = os.getenv("NODE_RED_API", "http://127.0.0.1:1880")
NODE_RED_API_KEY = os.getenv("NODE_RED_API_KEY", "")

def deploy_flows(flows: List[Dict[str, Any]], save_backup: bool = True) -> bool:
    """Deploy flows to Node-RED.
    
    Args:
        flows: List of flows to deploy
        save_backup: Whether to save a backup of the flows
        
    Returns:
        bool: True if deployment was successful
    """
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
            
        # Save backup if requested
        if save_backup:
            os.makedirs('node_red/backups', exist_ok=True)
            backup_path = os.path.join('node_red/backups', 'flows_backup.json')
            with open(backup_path, 'w') as f:
                json.dump(flows, f, indent=2)
            print(f"Backup saved to {backup_path}")
            
        # Deploy the flows
        deploy_response = requests.post(
            f"{NODE_RED_URL}/flows",
            headers=headers,
            json=flows
        )
        deploy_response.raise_for_status()
        
        print("Flows deployed successfully to Node-RED!")
        return True
        
    except requests.exceptions.ConnectionError:
        print("Error: Cannot connect to Node-RED. Make sure it's running.")
        return False
    except Exception as e:
        print(f"Error deploying flows: {str(e)}")
        return False
