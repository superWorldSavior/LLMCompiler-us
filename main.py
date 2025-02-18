"""Main application module."""
import os
import sys
from contextlib import asynccontextmanager
from typing import Dict, Any, AsyncGenerator, TypedDict, List, Optional

import gradio as gr
from fastapi import FastAPI
from loguru import logger
from openai import AsyncOpenAI

from llmcompiler.configs.ittpc.configs import CONFIGS as ITTPC_CONFIGS
from llmcompiler.src.llm_compiler.llm_compiler import LLMCompiler


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for FastAPI application.
    
    Handles startup and shutdown events.
    """
    # Startup
    logger.info("Starting application...")
    
    # Initialize OpenAI client
    openai_client = AsyncOpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
    )
    
    # Initialize LLM Compiler
    chain = LLMCompiler(
        tools=ITTPC_CONFIGS["tools"](),
        planner_llm=openai_client,
        planner_example_prompt=ITTPC_CONFIGS["prompts"]["gpt"]["planner_prompt"],
        planner_example_prompt_replan=None,
        planner_stop=None,
        planner_stream=True,
        agent_llm=openai_client,
        joinner_prompt=ITTPC_CONFIGS["prompts"]["gpt"]["output_prompt"],
        joinner_prompt_final=None,
        max_replans=ITTPC_CONFIGS["max_replans"],
        benchmark=False,
    )
    
    app.state.chain = chain
    logger.debug("Application components initialized")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.
    
    Returns:
        FastAPI: The configured FastAPI application
    """
    app = FastAPI(lifespan=lifespan)
    return app


def create_gradio_interface() -> gr.Interface:
    """Create the Gradio interface.
    
    Returns:
        gr.Interface: The configured Gradio interface
    """
    with gr.Blocks(title="Assistant Node-RED") as demo:
        gr.Markdown("# Assistant Node-RED")
        gr.Markdown("Je peux vous aider avec Node-RED, les données de température, la recherche d'informations et même vous raconter des blagues !")
        
        chatbot = gr.Chatbot()
        msg = gr.Textbox(label="Message")
        clear = gr.Button("Effacer")

        async def user(message: str, history: List[List[str]]) -> tuple[List[List[str]], str]:
            logger.info(f"Processing message: {message}")
            result = await app.state.chain.arun({"input": message})
            response = result["output"] if isinstance(result, dict) else str(result)
            logger.info(f"Response: {response}")
            history.append([message, response])
            return history, ""

        msg.submit(user, [msg, chatbot], [chatbot, msg])
        clear.click(lambda: None, None, chatbot, queue=False)

        gr.Examples(
            examples=[
                "Quelle est la température aujourd'hui ?",
                "Raconte-moi une blague et donne-moi la température d'hier.",
                "Cherche des informations sur les capteurs de température.",
            ],
            inputs=msg
        )

    return demo


# Create FastAPI app
app = create_app()

# Create and mount Gradio interface
demo = create_gradio_interface()
app = gr.mount_gradio_app(app, demo, path="/")


def main():
    """Run the FastAPI application."""
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    if not os.getenv("OPENAI_API_KEY"):
        print("Erreur : La variable d'environnement OPENAI_API_KEY n'est pas définie")
        exit(1)
    main()
