"""Chat agent implementation."""
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
from .models import ChatRequest, ChatResponse, Message, MessageHistory
from tools.tools_manager import ToolsManager
import logfire

# Configure logfire for project "test"
logfire.configure()
logger = logfire.Logfire()

class ChatDependencies(BaseModel):
    """Dependencies for the chat agent."""
    tools_manager: ToolsManager

    class Config:
        arbitrary_types_allowed = True


class ChatResult(BaseModel):
    """Result from the chat agent."""
    response: str = Field(description="Response to the user")
    tool_used: Optional[str] = Field(
        None,
        description="Name of the tool used, if any"
    )
    message_history: List[Dict[str, str]] = Field(
        default_factory=list,
        description="Updated conversation history"
    )


# Initialize the chat agent
chat_agent = Agent(
    'openai:gpt-4o-mini',
    deps_type=ChatDependencies,
    result_type=ChatResult,
    system_prompt=(
        'You are a helpful assistant that can use various tools to help users.\n\n'
        'Available tools:\n'
        '1. temperature - Query temperature measurements\n'
        '2. jokes - Tell jokes\n\n'
        'To use a tool, call use_tool with the exact tool name and your query.\n'
        'Example: use_tool("temperature", "list all temperatures")\n\n'
        'Always respond in French but keep technical terms in English.\n'
        'Use the appropriate tool when needed.'
    ),
)


@chat_agent.tool
async def use_tool(ctx: RunContext[ChatDependencies], tool: str, query: str) -> ChatResult:
    """Use a specific tool with the given query."""
    result = await ctx.deps.tools_manager.execute_tool(tool, query)
    
    # Fast path: si la réponse est directe, on la retourne sans reformatage
    if isinstance(result, ChatResponse) and result.direct_response:
        return ChatResult(
            response=result.response,
            tool_used=tool,
            message_history=result.message_history
        )
    
    # Sinon, on laisse l'agent formater la réponse
    return ChatResult(
        response=result,
        tool_used=tool,
        message_history=[]
    )
