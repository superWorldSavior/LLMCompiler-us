"""Temperature query tool implementation."""
from typing import Dict, Any, List, Union
import sqlite3
from datetime import datetime
from pydantic_ai import Agent, RunContext
from .models import (
    TemperatureMeasurement,
    MeasurementMetadata,
    TemperatureQuery,
    TemperatureResponse
)
from .dependencies import NodeREDDependencies
from .base_tool import BaseTool
import logfire

# Configure logfire
logfire.configure()
logger = logfire.Logfire()

class TemperatureQueryTool(BaseTool):
    """Tool for querying temperature measurements."""
    
    def __init__(self, **data):
        """Initialize temperature query tool."""
        super().__init__(**data)
        logger.info(f"Initializing temperature query tool: {self.name}")
        self._agent = self._create_agent()
    
    def _create_agent(self) -> Agent:
        """Create and configure the Pydantic AI agent for temperature queries."""
        logger.info("Creating temperature query agent...")
        agent = Agent(
            'openai:gpt-4o-mini',
            deps_type=NodeREDDependencies,
            result_type=Union[TemperatureResponse.Single, TemperatureResponse.List],
            system_prompt=(
                'You are a temperature query assistant. You help users query and analyze temperature measurements. '
                'You have access to two tools:\n'
                '1. get_temperature(date) to get temperature for a specific date\n'
                '2. list_temperatures(filter=None) to list all available temperatures with optional filters\n'
                'Use these tools to help users get temperature information.'
            ),
        )
        
        @agent.tool
        async def get_temperature(
            ctx: RunContext[NodeREDDependencies],
            date: str
        ) -> TemperatureResponse.Single:
            """Query temperature measurement for a specific date."""
            logger.info(f"Querying temperature for date: {date}")
            try:
                response = await ctx.deps.request(
                    endpoint="/query/temperature",
                    params={"date": date}
                )
                
                if "temperature" in response:
                    measurement = TemperatureMeasurement(
                        date=date,
                        temperature=response["temperature"]
                    )
                    metadata = MeasurementMetadata(
                        source="Node-RED",
                        timestamp=datetime.now().isoformat()
                    )
                    formatted_response = f"Temperature le {measurement.date}: {measurement.temperature}°C"
                    
                    return TemperatureResponse.Single(
                        success=True,
                        data=measurement,
                        metadata=metadata,
                        formatted_response=formatted_response
                    )
                else:
                    return TemperatureResponse.Single(
                        success=False,
                        error="Aucune donnée de température disponible pour cette date",
                        formatted_response="Aucune donnée de température disponible pour cette date"
                    )
                    
            except Exception as e:
                error_msg = f"Erreur lors de la requête: {str(e)}"
                logger.error(f"Error querying temperature: {str(e)}")
                return TemperatureResponse.Single(
                    success=False,
                    error=error_msg,
                    formatted_response=error_msg
                )
        
        @agent.tool
        async def list_temperatures(
            ctx: RunContext[NodeREDDependencies],
            filter: Dict[str, Any] = None
        ) -> TemperatureResponse.List:
            """List temperature measurements with optional filters."""
            logger.info("Listing temperatures", filter=filter)
            try:
                response = await ctx.deps.request(
                    endpoint="/list/temperatures",
                    params=filter
                )
                
                if "measurements" in response and isinstance(response["measurements"], list):
                    measurements = []
                    measurement_count = 0
                    logger.info("Processing measurements from Node-RED")
                    
                    for item in response["measurements"]:
                        try:
                            if "date" in item and "temperature" in item:
                                measurement = TemperatureMeasurement(
                                    date=item["date"],
                                    temperature=float(item["temperature"])
                                )
                                measurements.append(measurement)
                                measurement_count += 1
                            else:
                                logger.warning("Invalid measurement item structure", 
                                    missing_fields=[f for f in ["date", "temperature"] if f not in item]
                                )
                        except (ValueError, TypeError) as e:
                            logger.error("Failed to parse measurement", error=str(e))
                            continue
                    
                    if measurements:
                        metadata = MeasurementMetadata(
                            source="Node-RED",
                            timestamp=datetime.now().isoformat()
                        )
                        logger.info(f"Successfully processed {measurement_count} measurements")
                        
                        formatted_response = "Températures disponibles:\n" + "\n".join(
                            f"{m.date}: {m.temperature}°C"
                            for m in measurements
                        )
                        
                        return TemperatureResponse.List(
                            success=True,
                            data=measurements,
                            metadata=metadata,
                            filter_applied=filter,
                            formatted_response=formatted_response
                        )
                
                error_msg = "Aucune donnée de température disponible"
                logger.warning("No valid measurements found", 
                    response_type=type(response).__name__,
                    response_keys=list(response.keys()) if isinstance(response, dict) else None
                )
                return TemperatureResponse.List(
                    success=False,
                    error=error_msg,
                    filter_applied=filter,
                    formatted_response=error_msg
                )
                    
            except Exception as e:
                error_msg = f"Erreur lors de la requête: {str(e)}"
                logger.error(f"Error listing temperatures: {str(e)}")
                return TemperatureResponse.List(
                    success=False,
                    error=error_msg,
                    filter_applied=filter,
                    formatted_response=error_msg
                )
        
        return agent
    
    async def execute(self, query: str) -> str:
        """Execute the temperature query tool with the given query."""
        logger.info(f"Executing temperature query: {query}")
        try:
            deps = NodeREDDependencies()
            result = await self._agent.run(query, deps=deps)
            
            if hasattr(result, 'data'):
                data = result.data
                logger.info("Processing result data",
                    data_type=type(data).__name__,
                    success=getattr(data, 'success', None)
                )
                
                if data.success:
                    return data.formatted_response
                else:
                    raise ValueError(data.error or "Aucune donnée disponible")
            else:
                logger.error("Invalid response from agent", result=result)
                raise ValueError("Réponse invalide de l'agent")
        except Exception as e:
            logger.error("Error executing query", error=str(e))
            raise

# Export a singleton instance
temperature_tool = TemperatureQueryTool(
    name="temperature",
    description="Query temperature measurements"
)
