"""Main application module."""
import os
import sys
from typing import Dict, Any, AsyncGenerator, TypedDict, List, Optional

# Add src to PYTHONPATH
sys.path.append(os.path.join(os.path.dirname(__file__), "llmcompiler", "src"))

import gradio as gr
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from contextlib import asynccontextmanager
from langchain_community.chat_models import ChatOpenAI
from langchain_core.tools import Tool

# Import from llmcompiler package
from llmcompiler.src.llm_compiler.llm_compiler import LLMCompiler
from llmcompiler.src.utils.logger_utils import enable_logging

# Configure logging
logger.remove()
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="DEBUG"
)

# Activer le logging pour voir le graphe de dépendances
enable_logging(True)

# Outils personnalisés
async def get_weather(city: str) -> str:
    return f"La température à {city} est de 20°C"

async def get_population(city: str) -> str:
    return f"La population de {city} est de 1 million d'habitants"

def generate_tools() -> List[Tool]:
    """Générer la liste des outils disponibles."""
    return [
        Tool(
            name="weather",
            func=get_weather,
            description=(
                "weather(city: str) -> str:\n"
                " - Obtient la météo pour une ville donnée\n"
                " - Retourne la température\n"
            ),
            stringify_rule=lambda args: f"weather({args[0]})",
        ),
        Tool(
            name="population",
            func=get_population,
            description=(
                "population(city: str) -> str:\n"
                " - Obtient la population d'une ville\n"
                " - Retourne le nombre d'habitants\n"
            ),
            stringify_rule=lambda args: f"population({args[0]})",
        ),
    ]

# Prompts
PLANNER_PROMPT = '''
Question: Quelle est la température et la population à Paris ?
1. weather("Paris")
2. population("Paris")
3. join()
###

Question: Quelle ville a la plus grande population entre Lyon et Marseille ?
1. population("Lyon")
2. population("Marseille")
3. join()
###
'''

JOINER_PROMPT = '''
Solve a question answering task with interleaving Observation, Thought, and Action steps.
Here are some guidelines:
  - You will be given a Question and some API results, which are the Observations.
  - Thought needs to reason about the question based on the Observations.
  - Your final answer should be concise and direct.
  - If you need more information to answer the question properly, use Replan.

Action can be of two types:
 (1) Finish(answer): returns the answer and finishes the task
 (2) Replan(reason): requests a new plan with the given reason

Here are some examples:

Question: Quelle est la température et la population à Paris ?
weather("Paris")
Observation: La température à Paris est de 20°C
population("Paris")
Observation: La population de Paris est de 1 million d'habitants
Thought: J'ai obtenu la température et la population de Paris.
Action: Finish(La température est de 20°C et la population est de 1 million d'habitants)

Question: Quelle ville est la plus chaude entre Paris et Lyon ?
weather("Paris")
Observation: La température à Paris est de 20°C
Thought: Je n'ai que la température de Paris, j'ai besoin de celle de Lyon pour comparer.
Action: Replan(Il faut aussi obtenir la température de Lyon pour faire la comparaison)

Question: {question}
{scratchpad}
'''

def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        """Lifespan manager for FastAPI app."""
        logger.info("Starting application...")
        
        # Initialiser le modèle LLM
        llm = ChatOpenAI(
            model_name="gpt-3.5-turbo",
            temperature=0,
            streaming=True,
        )
        
        # Créer l'instance du LLM Compiler
        compiler = LLMCompiler(
            tools=generate_tools(),
            planner_llm=llm,
            planner_example_prompt=PLANNER_PROMPT,
            planner_example_prompt_replan=None,
            planner_stop=None,
            planner_stream=True,
            agent_llm=llm,
            joinner_prompt=JOINER_PROMPT,
            joinner_prompt_final=None,
            max_replans=2,
            benchmark=False,
        )
        
        app.state.compiler = compiler
        logger.debug("Application components initialized")
        yield
        logger.info("Shutting down application...")
    
    app = FastAPI(lifespan=lifespan)
    return app

# Create FastAPI app
app = create_app()

async def process_message(message: str, history: List[List[str]]) -> str:
    """Process a message using the LLM Compiler."""
    try:
        result = await app.state.compiler.acall({"input": message})
        return result["output"]
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        return f"Désolé, une erreur s'est produite : {str(e)}"

def create_gradio_interface():
    """Create the Gradio interface."""
    with gr.Blocks() as demo:
        chatbot = gr.Chatbot(
            label="Chat",
            height=500,
            placeholder="Assistant IA - Je peux vous aider avec la météo et les données démographiques",
        )
        
        msg = gr.Textbox(
            show_label=False,
            placeholder="Entrez votre message ici...",
            container=True
        )

        async def respond(message, chat_history):
            if not message:
                return "", chat_history
            
            bot_message = await process_message(message, chat_history)
            chat_history.append((message, bot_message))
            return "", chat_history

        msg.submit(respond, [msg, chatbot], [msg, chatbot])
        
    return demo

# Create and mount Gradio interface
demo = create_gradio_interface()
app = gr.mount_gradio_app(app, demo, path="/")

def main():
    """Run the FastAPI application."""
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)

if __name__ == "__main__":
    if not os.getenv("OPENAI_API_KEY"):
        print("Erreur : La variable d'environnement OPENAI_API_KEY n'est pas définie")
        exit(1)
    main()
