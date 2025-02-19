"""Main application module."""
import os
import sys
import json
from contextlib import asynccontextmanager
from typing import Dict, Any, Optional

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import logging
from typing import Optional
import json
import time
import traceback

from loguru import logger
from pydantic import BaseModel

from llmcompiler.src.llm_compiler.llm_compiler import LLMCompiler
from llmcompiler.src.llm_compiler.constants import END_OF_PLAN
from llmcompiler.src.callbacks.callbacks import AsyncStatsCallbackHandler
from llmcompiler.configs.ittpc.configs import CONFIGS as ITTPC_CONFIGS
from llmcompiler.src.utils.model_utils import get_model
from llmcompiler.src.utils.logger_utils import log, enable_logging

# Enable logging
enable_logging(True)

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
    log("🚀 Starting application...")
    
    # Initialize LLMs using their utils
    log("🔧 Initializing LLMs...")
    
    # Agent LLM - no streaming
    agent_llm = get_model(
        model_type="openai",
        model_name="gpt-4",
        vllm_port=None,
        stream=False,
        temperature=0
    )
    
    # Planner LLM - with streaming
    planner_llm = get_model(
        model_type="openai",
        model_name="gpt-4",
        vllm_port=None,
        stream=True,
        temperature=0
    )

    # Initialize LLM Compiler
    log("🔧 Initializing LLM Compiler...")
    chain = LLMCompiler(
        tools=ITTPC_CONFIGS["tools"](),
        planner_llm=planner_llm,
        planner_example_prompt=ITTPC_CONFIGS["prompts"]["gpt"]["planner_prompt"],
        planner_example_prompt_replan=None,
        planner_stop=[END_OF_PLAN],
        planner_stream=True,
        agent_llm=agent_llm,
        joinner_prompt=ITTPC_CONFIGS["prompts"]["gpt"]["output_prompt"],
        joinner_prompt_final=None,
        max_replans=2,
        benchmark=True,
    )
    
    app.state.chain = chain
    log("✅ Application components initialized")
    
    yield
    
    # Shutdown
    log("👋 Shutting down application...")


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
        log("🔌 New WebSocket connection request")
        await websocket.accept()
        log("✅ WebSocket connection accepted")
        
        try:
            while True:
                # Receive message from client
                message = await websocket.receive_text()
                log("📩 Received message:", message)
                
                try:
                    # Process message with LLMCompiler
                    log("🤖 Processing with LLMCompiler (streaming mode)...")
                    
                    # Initialize callback handler with streaming
                    stats_handler = AsyncStatsCallbackHandler(stream=True)
                    
                    start_time = time.time()
                    try:
                        log("Question:", block=True)
                        log(message, block=True)
                        
                        response = await app.state.chain.arun(
                            message,
                            callbacks=[stats_handler]
                        )
                        
                        # Calculate processing time
                        processing_time = f"{time.time() - start_time:.2f}"
                        
                        # Log stats
                        log("Raw Answer:", block=True)
                        log(response, block=True)
                        log("Break out of replan loop.")
                        log("> Finished chain.")
                        
                        stats = stats_handler.get_stats()
                        log(f"📊 Stats: {stats}")
                        log(f"⏱️ Processing time: {processing_time} seconds")
                        
                        # Use response - extract answer from tuple (thought, answer, is_replan)
                        if isinstance(response, tuple) and len(response) == 3:
                            _, response_text, _ = response
                        else:
                            response_text = str(response)
                        
                        response_text = response_text.strip()
                        
                        # Send final response
                        await websocket.send_json({
                            "type": "response",
                            "text": response_text,
                            "icon": "",
                            "time": processing_time,
                            "error": False
                        })
                        
                    except Exception as e:
                        log(f"❌ Error in chain: {str(e)}")
                        log(traceback.format_exc())
                        await websocket.send_json({
                            "type": "response",
                            "text": f"Une erreur s'est produite : {str(e)}",
                            "icon": "❌",
                            "time": "0",
                            "error": True
                        })
                    
                except Exception as e:
                    log(f"❌ Processing error: {str(e)}")
                    await websocket.send_json({
                        "type": "response",
                        "text": f"Une erreur s'est produite : {str(e)}",
                        "icon": "❌",
                        "time": "0",
                        "error": True
                    })
                
        except Exception as e:
            log(f"❌ WebSocket error: {str(e)}")
            log(traceback.format_exc())
            
        finally:
            await websocket.close()
    
    return app


def main():
    """Run the FastAPI application."""
    import uvicorn
    log("🌟 Starting server...")
    # Create FastAPI app
    app = create_app()
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    if not os.getenv("OPENAI_API_KEY"):
        log("❌ OPENAI_API_KEY environment variable is not set")
        sys.exit(1)
    main()
