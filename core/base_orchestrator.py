"""Base models and types for the orchestrator."""
from typing import Dict, Any, List, Optional, Literal, Tuple, Annotated
import operator
from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict


class Message(TypedDict):
    """A message in the conversation."""
    role: Literal["user", "assistant", "error"]
    content: str


class Plan(TypedDict):
    """Plan to follow in future."""
    steps: List[str]  # different steps to follow, should be in sorted order


class PlanExecute(TypedDict):
    """The state for plan-and-execute workflow."""
    input: str
    plan: List[str]
    past_steps: Annotated[List[Tuple[str, str]], operator.add]  # List of (task, response)
    response: str


class ChatRequest(TypedDict):
    """A request from the user."""
    message: str
    message_history: Optional[List[Message]]


class ChatResponse(TypedDict):
    """A response from the agent."""
    response: str  # Always a string
    message_history: List[Message]
