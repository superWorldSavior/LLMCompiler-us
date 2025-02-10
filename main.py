"""Main application module."""
import os
from typing import Dict, Any
import gradio as gr
from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from core.chat import ChatDependencies, chat_agent
from core.models import ChatRequest, ChatResponse
from tools.tools_manager import ToolsManager
import logfire
import json

# Configure logfire for project "test"
logfire.configure()
logger = logfire.Logfire()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan manager for FastAPI app."""
    logger.info("Starting application...")
    tools_manager = ToolsManager()  # Fixed: Create new instance
    app.state.tools_manager = tools_manager
    yield
    logger.info("Shutting down application...")

app = FastAPI(lifespan=lifespan)


def create_gradio_interface():
    """Create the Gradio interface."""
    logger.info("Creating Gradio interface...")
    
    with gr.Blocks() as demo:
        chatbot = gr.Chatbot()
        msg = gr.Textbox()
        clear = gr.Button("Clear")
        
        async def user(user_message, history):
            logger.info(f"Processing chat message: {user_message}")
            try:
                response = await chat(ChatRequest(message=user_message))
                logger.info(f"Chat response: {response}")
                return "", history + [[user_message, response["response"]]]
            except Exception as e:
                logger.error(f"Error processing message: {str(e)}")
                return "", history + [(user_message, f"Error: {str(e)}")]
            
        msg.submit(user, [msg, chatbot], [msg, chatbot])
        clear.click(lambda: None, None, chatbot, queue=False)
    
    return demo


@app.post("/chat")
async def chat(message: ChatRequest) -> Dict[str, Any]:
    """Chat endpoint.
    
    Args:
        message: The chat request
        
    Returns:
        Chat response
    """
    logger.info(f"Received chat request: {message}")
    try:
        # Run the chat agent with dependencies
        result = await chat_agent.run(
            message.message,
            deps=ChatDependencies(tools_manager=app.state.tools_manager)
        )
        
        response = {
            "response": str(result.data.response) if result.data and result.data.response else "",
            "tool_used": result.data.tool_used if result.data and result.data.tool_used else None,
            "message_history": result.data.message_history if result.data and result.data.message_history else []
        }
        
        logger.info("Chat response", response=response)
        
        return response
        
    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


if __name__ == "__main__":
    import uvicorn
    
    # Create Gradio interface
    demo = create_gradio_interface()
    app = gr.mount_gradio_app(app, demo, path="/")
    
    # Run the app
    uvicorn.run(app, host="0.0.0.0", port=8000)
