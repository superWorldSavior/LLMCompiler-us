"""Main application module."""
import os
import sys
import json
from contextlib import asynccontextmanager
from typing import Dict, Any, Optional

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from pydantic import BaseModel
from langchain_openai import ChatOpenAI

from llmcompiler.configs.ittpc.configs import CONFIGS as ITTPC_CONFIGS
from llmcompiler.src.llm_compiler.llm_compiler import LLMCompiler
from llmcompiler.src.llm_compiler.constants import END_OF_PLAN


# Configure loguru
logger.remove()  # Remove default handler
logger.add(sys.stdout, format="<green>{time:HH:mm:ss}</green> | {level} | <blue>{message}</blue>")


class ChatRequest(BaseModel):
    message: str


class ChatMessage(BaseModel):
    type: str  # 'thought', 'response', 'error'
    text: str
    icon: Optional[str] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for FastAPI application.
    
    Handles startup and shutdown events.
    """
    # Startup
    logger.info("🚀 Starting application...")
    
    # Initialize OpenAI client
    logger.info("🔧 Initializing OpenAI client...")
    llm = ChatOpenAI(
        model_name=ITTPC_CONFIGS["default_model"],
        temperature=0,
        streaming=True,
    )
    
    # Initialize LLM Compiler with configuration from ITTPC_CONFIGS
    logger.info("🔧 Initializing LLM Compiler...")
    chain = LLMCompiler(
        tools=ITTPC_CONFIGS["tools"](),
        planner_llm=llm,
        agent_llm=llm,
        planner_example_prompt=ITTPC_CONFIGS["prompts"]["gpt"]["planner_prompt"],
        planner_example_prompt_replan=None,
        planner_stop=None,
        planner_stream=True,
        joinner_prompt=ITTPC_CONFIGS["prompts"]["gpt"]["output_prompt"],
        joinner_prompt_final=None,
        max_replans=ITTPC_CONFIGS["max_replans"],
        benchmark=False
    )
    
    app.state.chain = chain
    logger.info("✅ Application components initialized")
    
    yield
    
    # Shutdown
    logger.info("👋 Shutting down application...")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.
    
    Returns:
        FastAPI: The configured FastAPI application
    """
    app = FastAPI(lifespan=lifespan)
    
    # Add CORS middleware to allow requests from Svelte frontend
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, replace with your frontend URL
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    @app.websocket("/ws/chat")
    async def websocket_chat(websocket: WebSocket):
        """WebSocket endpoint for chat.
        
        Handles real-time chat communication with the client.
        """
        logger.info("🔌 New WebSocket connection request")
        await websocket.accept()
        logger.info("✅ WebSocket connection accepted")
        
        try:
            while True:
                # Receive message from client
                message = await websocket.receive_text()
                logger.info(f"📩 Received message: {message}")
                
                try:
                    # Process message with LLMCompiler
                    logger.info("🤖 Processing with LLMCompiler...")
                    response = await app.state.chain.arun({"input": message})
                    logger.info(f"📝 Raw response: {response}")
                    
                    final_msg = {
                        "type": "response",
                        "text": response,
                        "icon": ""
                    }
                    await websocket.send_text(json.dumps(final_msg))
                
                except Exception as e:
                    logger.error(f"❌ Processing error: {str(e)}")
                    error_msg = {
                        "type": "error",
                        "text": f"Une erreur est survenue : {str(e)}",
                        "icon": "⚠️"
                    }
                    await websocket.send_text(json.dumps(error_msg))
                
        except Exception as e:
            logger.error(f"❌ WebSocket error: {str(e)}")
            await websocket.close()
    
    return app


def main():
    """Run the FastAPI application."""
    import uvicorn
    logger.info("🌟 Starting server...")
    # Create FastAPI app
    app = create_app()
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    if not os.getenv("OPENAI_API_KEY"):
        logger.error("❌ OPENAI_API_KEY environment variable is not set")
        sys.exit(1)
    main()
