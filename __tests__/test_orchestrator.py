"""Tests for the orchestrator."""
import pytest
from loguru import logger
from typing import Dict, Any, Optional, TypedDict
from unittest.mock import AsyncMock, MagicMock
import json

from core.base_orchestrator import ChatRequest, ChatResponse, Plan
from core.orchestrator import Orchestrator
from core.llm_manager import LLMManager
from tools.base_tool import Tool, ToolConfig, ToolResponse
from tools.tools_manager import ToolsManager


class DummyTool:
    """A dummy tool that just says hello."""
    
    def __init__(self):
        self.config = {
            "name": "dummy",
            "description": "Un tool qui dit bonjour",
            "category": "test",
            "enabled": True,
            "required_parameters": [{
                "name": "name",
                "description": "Nom de la personne à saluer",
                "required": True
            }],
            "tool_dependencies": []
        }
    
    async def validate_dependencies(self) -> bool:
        """No dependencies needed."""
        return True
        
    async def execute(
        self,
        query: str,
        parameters: Optional[Dict[str, Any]] = None
    ) -> str:
        """Execute the tool.
        
        Args:
            query: Query to execute
            parameters: Optional parameters
            
        Returns:
            Tool response as JSON string
        """
        response: ToolResponse = {
            "success": True,
            "data": {"message": "Bonjour!"},
            "error": None
        }
        return json.dumps(response)


Tool.register(DummyTool)


class MockLLMManager:
    """Mock LLM manager for testing."""
    
    def __init__(self):
        """Initialize the mock LLM manager."""
        self.llm = MagicMock()
        self.llm.model_name = "mock-model"
        
    async def plan(self, prompt: str) -> Dict[str, Any]:
        """Return a mock plan."""
        return {
            "steps": [
                {
                    "tool": "dummy",
                    "parameters": {"name": "test"},
                    "thought": "Je vais utiliser le dummy tool pour dire bonjour",
                    "action": "Exécuter le dummy tool"
                }
            ],
            "response": "Je vais vous dire bonjour.",
            "past_steps": []
        }
        
    async def execute(self, prompt: str) -> str:
        """Execute a step from the plan."""
        return "Hello test!"


@pytest.fixture
def mock_llm_manager():
    """Create a mock LLM manager."""
    return MockLLMManager()


@pytest.fixture
def mock_tools_manager():
    """Create a mock tools manager."""
    return ToolsManager()


@pytest.fixture
def orchestrator(mock_llm_manager, mock_tools_manager):
    """Create an orchestrator with mock dependencies."""
    return Orchestrator(
        llm_manager=mock_llm_manager,
        tools_manager=mock_tools_manager
    )


@pytest.mark.asyncio
async def test_orchestrator_plan_and_execute(orchestrator):
    """Test that the orchestrator can plan and execute steps."""
    request: ChatRequest = {
        "message": "Bonjour! Comment vas-tu?",
        "message_history": []
    }
    
    response = await orchestrator.process_request(request)
    
    assert response["response"]
    assert len(response["message_history"]) > 0
    assert not any("error" in msg["role"] for msg in response["message_history"])
