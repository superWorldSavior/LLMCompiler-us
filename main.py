"""Main application module."""
import os
from typing import Dict, Any, AsyncGenerator
import gradio as gr
from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
import sys
from contextlib import asynccontextmanager
from core.base_orchestrator import ChatRequest, ChatResponse, Message, PlanExecute
from tools.tools_manager import ToolsManager
from core.orchestrator import Orchestrator
from core.llm_manager import LLMManager
import json

# Configure logging - with better error tracking
logger.remove()  # Remove default handler
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="DEBUG"  # Set to DEBUG level
)
logger.add(
    "app.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}\n{exception}",
    rotation="10 MB",
    level="DEBUG",  # Set to DEBUG level
    backtrace=True,
    diagnose=True
)

def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        """Lifespan manager for FastAPI app."""
        logger.info("Starting application...")
        tools_manager = ToolsManager()
        llm_manager = LLMManager(tools_manager=tools_manager)
        orchestrator = Orchestrator(tools_manager=tools_manager, llm_manager=llm_manager)
        app.state.tools_manager = tools_manager
        app.state.orchestrator = orchestrator
        logger.debug("Application components initialized", 
                    tools=tools_manager.list_tools())
        yield
        logger.info("Shutting down application...")
    
    app = FastAPI(lifespan=lifespan)
    return app

# Create FastAPI app
app = create_app()

def create_gradio_interface(app: FastAPI):
    """Create the Gradio interface."""
    logger.info("Creating Gradio interface...")
    
    with gr.Blocks() as demo:
        chatbot = gr.Chatbot(
            label="Chat",
            type="messages",
            height=500,
            placeholder="<strong>Assistant IA</strong><br>Je peux vous aider avec les températures et les blagues Chuck Norris",
            container=True,
            scale=4
        )
        with gr.Row():
            msg = gr.Textbox(
                show_label=False,
                placeholder="Entrez votre message ici...",
                container=False,
                scale=7
            )
            submit = gr.Button("Envoyer", scale=1)
            clear = gr.Button("Clear", scale=1)
        
        async def user(user_message: str, history: list) -> AsyncGenerator[tuple[str, list], None]:
            """Process user message and stream responses."""
            try:
                logger.info("Processing user message", message=user_message)
                
                # Add user message to history with OpenAI format
                history.append({"role": "user", "content": user_message})
                yield "", history
                
                try:
                    # Create initial state
                    state = {"input": user_message, "plan": [], "past_steps": [], "response": ""}
                    logger.debug("Created initial state", state=state)
                    
                    # Process request through workflow with streaming
                    async for event in app.state.orchestrator.workflow.astream(
                        state,
                        {"stream_events": ["messages", "values"]}
                    ):
                        logger.debug("Stream event received", event=event)
                        if event.get("response"):
                            # Update last message with assistant response
                            history.append({"role": "assistant", "content": event["response"]})
                            yield "", history
                    
                except Exception as e:
                    logger.exception("Error during stream processing")
                    history.append({"role": "assistant", "content": f"Erreur pendant le traitement de la requête: {str(e)}"})
                    yield "", history
                    return
                
                # Final response if not already set
                if not history[-1].get("content"):
                    history.append({"role": "assistant", "content": event.get("response", "Pas de réponse")})
                    yield "", history
                
            except Exception as e:
                logger.exception("Unhandled error in chat processing")
                history.append({"role": "assistant", "content": f"Erreur interne du serveur: {str(e)}"})
                yield "", history
        
        # Submit events
        submit.click(fn=user, inputs=[msg, chatbot], outputs=[msg, chatbot])
        msg.submit(fn=user, inputs=[msg, chatbot], outputs=[msg, chatbot])
        clear.click(fn=lambda: None, inputs=None, outputs=chatbot, queue=False)
        
    return demo

@app.post("/chat")
async def chat(message: ChatRequest) -> Dict[str, Any]:
    """Chat endpoint."""
    logger.debug("Chat request received", message=message)
    try:
        # Create initial state
        state = {"input": message.message, "plan": [], "past_steps": [], "response": ""}
        logger.debug("Created initial state", state=state)
        
        # Process request through workflow
        final_state = await app.state.orchestrator.workflow.ainvoke(state)
        logger.debug("Got final state", state=final_state)
        
        return final_state
    except Exception as e:
        logger.exception("Chat request error",
                        error=str(e),
                        message=message,
                        state=state if 'state' in locals() else None)
        raise HTTPException(status_code=500, detail=str(e))

# Create and mount Gradio interface
demo = create_gradio_interface(app)
app = gr.mount_gradio_app(app, demo, path="/")

def main():
    """Run the FastAPI application."""
    import uvicorn
    logger.debug("Starting uvicorn server")
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()
