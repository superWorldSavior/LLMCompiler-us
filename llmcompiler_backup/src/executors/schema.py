from pydantic import BaseModel
from typing import Dict, List, Optional


class Step(BaseModel):
    """Step."""

    value: str
    """The value."""


class Plan(BaseModel):
    """Plan."""

    steps: List[Step]
    """The steps."""


class StepResponse(BaseModel):
    """Step response."""

    response: str
    """The response."""
