from flows.temperature_flow import TemperatureFlow
from flows.jokes_flow import JokesFlow
from flows.temperature_list_flow import TemperatureListFlow
from utils.node_red import deploy_flows

def main():
    """Deploy all flows to Node-RED."""
    # Initialize flows
    all_flows = []
    
    # Add Temperature flow
    temperature_flow = TemperatureFlow()
    all_flows.extend(temperature_flow.generate())
    
    # Add Jokes flow
    jokes_flow = JokesFlow()
    all_flows.extend(jokes_flow.generate())
    
    # Add Temperature List flow
    temp_list_flow = TemperatureListFlow()
    all_flows.extend(temp_list_flow.generate())
    
    # Deploy all flows
    deploy_flows(all_flows)

if __name__ == "__main__":
    main()
