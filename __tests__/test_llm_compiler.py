"""Test LLMCompiler functionality."""
import asyncio
import os
from typing import Dict, Any

from langchain_openai import ChatOpenAI

from llmcompiler.configs.ittpc.configs import CONFIGS as ITTPC_CONFIGS
from llmcompiler.src.llm_compiler.llm_compiler import LLMCompiler


async def test_llm_compiler_basic_query():
    """Test that LLMCompiler can handle a basic query."""
    # Initialize OpenAI client
    llm = ChatOpenAI(
        model_name="gpt-3.5-turbo",
        temperature=0,
        streaming=True,
    )
    
    # Initialize LLM Compiler
    chain = LLMCompiler(
        tools=ITTPC_CONFIGS["tools"](),
        planner_llm=llm,
        planner_example_prompt=ITTPC_CONFIGS["prompts"]["gpt"]["planner_prompt"],
        planner_example_prompt_replan=None,
        planner_stop=None,
        planner_stream=True,
        agent_llm=llm,
        joinner_prompt=ITTPC_CONFIGS["prompts"]["gpt"]["output_prompt"],
        joinner_prompt_final=None,
        max_replans=ITTPC_CONFIGS["max_replans"],
        benchmark=False,
    )
    
    # Test simple query
    query = "Quelle est la température aujourd'hui ?"
    try:
        print(f"\nSending query: {query}")
        result = await chain.arun({"input": query})
        print(f"Received result: {result}")
        
        # Assertions - handle both string and dict responses
        if isinstance(result, Dict):
            assert "output" in result, "Result dictionary should have an 'output' key"
            assert isinstance(result["output"], str), "Output should be a string"
            response_text = result["output"]
        else:
            assert isinstance(result, str), "Result should be a string if not a dictionary"
            response_text = result
            
        print(f"\nResponse text: {response_text}")
        print("\nTest passed successfully!")
        return result
    except Exception as e:
        print(f"\nTest failed with error: {str(e)}")
        raise


if __name__ == "__main__":
    if not os.getenv("OPENAI_API_KEY"):
        print("Erreur : La variable d'environnement OPENAI_API_KEY n'est pas définie")
        exit(1)
        
    # Run the test
    result = asyncio.run(test_llm_compiler_basic_query())
    print(f"\nFinal result: {result}")
