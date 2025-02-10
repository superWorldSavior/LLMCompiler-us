"""Core models for chat functionality."""

from datetime import datetime
from typing import List, Dict, Optional
from pydantic import BaseModel, Field


class Message(BaseModel):
    """Model for chat messages."""
    role: str = Field(..., description="Role of the message sender (user or assistant)")
    content: str = Field(..., description="Content of the message")
    timestamp: datetime = Field(default_factory=datetime.now)


class MessageHistory(BaseModel):
    """Model for chat message history."""
    messages: List[Message] = Field(default_factory=list)
    max_messages: int = Field(default=10, description="Maximum number of messages to keep")

    def add_message(self, role: str, content: str):
        """Add a new message to the history."""
        self.messages.append(Message(role=role, content=content))
        if len(self.messages) > self.max_messages:
            self.messages.pop(0)  # Remove oldest message

    def get_context(self) -> str:
        """Get conversation context as a formatted string."""
        return "\n".join([f"{m.role}: {m.content}" for m in self.messages])


class ChatRequest(BaseModel):
    """Model for chat requests."""
    message: str
    message_history: Optional[List[Dict[str, str]]] = Field(
        None,
        description="Previous messages in the conversation"
    )


class ChatResponse(BaseModel):
    """Model for chat responses."""
    response: str
    message_history: List[Dict[str, str]] = Field(
        default_factory=list,
        description="Updated conversation history"
    )
    direct_response: bool = Field(
        default=False,
        description="If True, skip agent reformatting"
    )
