"""Models for tools responses."""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class JokeResult(BaseModel):
    """Model for joke responses."""
    success: bool = Field(description="Whether the joke was successfully retrieved")
    joke: Optional[str] = Field(None, description="The Chuck Norris joke text")
    error: Optional[str] = Field(None, description="Error message if joke retrieval failed")


# Temperature Models
class TemperatureMeasurement(BaseModel):
    """Model for a single temperature measurement."""
    date: str = Field(description="Date of measurement in YYYY-MM-DD format")
    temperature: float = Field(description="Temperature in Celsius")


class MeasurementMetadata(BaseModel):
    """Model for measurement metadata."""
    timestamp: str = Field(description="Time of the query")
    source: str = Field(description="Source of the data")


class TemperatureQuery:
    """Models for temperature queries."""
    
    class Single(BaseModel):
        """Query for a single temperature measurement."""
        date: str = Field(description="Date to query in YYYY-MM-DD format")
    
    class List(BaseModel):
        """Query for a list of temperature measurements with optional filters."""
        filter: Optional[Dict[str, Any]] = Field(
            default=None,
            description="Optional filters to apply to the query"
        )


class TemperatureResponse:
    """Models for temperature responses."""
    
    class Base(BaseModel):
        """Base response model with common fields."""
        success: bool = Field(description="Whether the query was successful")
        metadata: Optional[MeasurementMetadata] = Field(
            None,
            description="Query metadata"
        )
        error: Optional[str] = Field(
            None,
            description="Error message if query failed"
        )
        formatted_response: Optional[str] = Field(
            None,
            description="Pre-formatted response string in French"
        )
    
    class Single(Base):
        """Response for a single temperature query."""
        data: Optional[TemperatureMeasurement] = Field(
            None,
            description="Single temperature measurement"
        )
    
    class List(Base):
        """Response for a temperature list query."""
        data: Optional[List[TemperatureMeasurement]] = Field(
            None,
            description="List of temperature measurements"
        )
        filter_applied: Optional[Dict[str, Any]] = Field(
            None,
            description="Filters that were applied to the query"
        )
