from abc import ABC, abstractmethod
from typing import Dict, List, Any
import uuid

class NodeRedFlow(ABC):
    """Base class for Node-RED flows."""
    
    def __init__(self):
        """Initialize flow with a unique tab ID."""
        self.tab_id = f"flow_{str(uuid.uuid4())[:8]}"
        
    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the flow."""
        pass
        
    @property
    @abstractmethod
    def description(self) -> str:
        """Description of the flow."""
        pass
    
    def create_tab(self) -> Dict[str, Any]:
        """Create the tab node for this flow."""
        return {
            "id": self.tab_id,
            "type": "tab",
            "label": self.name,
            "disabled": False,
            "info": self.description
        }
    
    @abstractmethod
    def generate_nodes(self) -> List[Dict[str, Any]]:
        """Generate the nodes for this flow."""
        pass
        
    def generate(self) -> List[Dict[str, Any]]:
        """Generate the complete flow including tab and nodes."""
        flow = [self.create_tab()]
        flow.extend(self.generate_nodes())
        return flow
