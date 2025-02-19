"""Configuration for ITTPC LLMCompiler."""
from .gpt_prompts import PLANNER_PROMPT, OUTPUT_PROMPT
from .tools import generate_tools

CONFIGS = {
    "default_model": "gpt-4o-mini",
    "prompts": {
        "gpt": {
            "planner_prompt": PLANNER_PROMPT,
            "output_prompt": OUTPUT_PROMPT,
        },
    },
    "tools": generate_tools,
    "max_replans": 2,
}