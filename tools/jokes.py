"""Jokes tool implementation."""
import requests
from pydantic_ai import Agent, RunContext
from .dependencies import NodeREDDependencies
from .models import JokeResult
from .base_tool import BaseTool

class JokesTool(BaseTool):
    """Tool for fetching and telling Chuck Norris jokes in French."""
    
    def _create_agent(self) -> Agent:
        """Create and configure the Pydantic AI agent for jokes."""
        agent = Agent(
            'openai:gpt-4o-mini',
            deps_type=NodeREDDependencies,
            result_type=JokeResult,
            system_prompt=(
                'You are a friendly assistant that tells Chuck Norris jokes in French. '
                'You have access to tools to fetch jokes and you should use them when appropriate.'
            ),
        )
        
        # Register the get_joke tool with the agent
        @agent.tool
        async def get_joke(ctx: RunContext[NodeREDDependencies]) -> JokeResult:
            """Fetches a random Chuck Norris joke from Node-RED API."""
            try:
                url = f"{ctx.deps.api_url}{ctx.deps.endpoint}"
                response = requests.get(url)
                response.raise_for_status()
                joke = response.json()["joke"]
                return JokeResult(success=True, joke=joke)
            except Exception as e:
                return JokeResult(success=False, error=str(e))
        
        return agent
    
    async def execute(self, query: str) -> str:
        """Execute the jokes tool with the given query.
        
        Args:
            query: The input query for the tool
            
        Returns:
            A Chuck Norris joke in French
        """
        result = await self.agent.run(query)
        if result.data.success:
            return result.data.joke
        else:
            raise ValueError(result.data.error or "Failed to get joke")

# Export a singleton instance
jokes_tool = JokesTool(
    name="jokes",
    description="Fetches and tells Chuck Norris jokes in French"
)
