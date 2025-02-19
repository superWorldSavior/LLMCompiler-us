"""Tools configuration for ITTPC."""
from typing import Any, List, Optional, Dict

from llmcompiler.src.tools.base import Tool as LLMCompilerTool
from tools.node_red_tools import NodeREDStatusTool, TemperatureTool
from tools.base_tool import ToolConfig
from tools.jokes_tools import ChuckNorrisJokeTool
from llmcompiler.src.docstore.r2r_rag import R2RDocstore, R2RExplorer
from pydantic import BaseModel


# Initialize R2R docstore and explorer
r2r_docstore = R2RDocstore(benchmark=True, char_limit=1000)
r2r_explorer = R2RExplorer(r2r_docstore)

class TableOutput(BaseModel):
    """Output format for table data."""
    headers: List[str]
    rows: List[List[str]]

    def format(self) -> str:
        """Format the table data for the LLM output."""
        headers_str = ",".join(self.headers)
        rows_str = "|".join([",".join(row) for row in self.rows])
        return f"Table: headers={headers_str}|{rows_str}"


class CreateTableTool:
    """Tool for creating formatted tables."""

    def __init__(self, config: ToolConfig):
        self.config = config

    async def execute(self, input: str, parameters: Dict[str, Any]) -> str:
        """Create a formatted table string."""
        headers = parameters.get("headers", [])
        rows = parameters.get("rows", [])
        table = TableOutput(headers=headers, rows=rows)
        return table.format()

async def node_red_status() -> str:
    """Get Node-RED status."""
    tool = NodeREDStatusTool(ToolConfig(
        name="node_red_status",
        description="Get Node-RED status",
        category="node_red"
    ))
    result = await tool.execute("")
    return result

async def get_temperature(date: Optional[str] = None, start_date: Optional[str] = None, end_date: Optional[str] = None) -> str:
    """Get temperature data."""
    tool = TemperatureTool(ToolConfig(
        name="temperature",
        description="Get temperature data",
        category="node_red"
    ))
    parameters = {}
    if date:
        parameters["date"] = date
    if start_date:
        parameters["start_date"] = start_date
    if end_date:
        parameters["end_date"] = end_date
    
    result = await tool.execute("", parameters)
    return result

async def get_chuck_norris_joke() -> str:
    """Get a random Chuck Norris joke."""
    tool = ChuckNorrisJokeTool(ToolConfig(
        name="chuck_norris_joke",
        description="Get a random Chuck Norris joke",
        category="fun"
    ))
    result = await tool.execute("")
    return result

async def search_knowledge(query: str, top_k: int = 5) -> str:
    """Search in R2R knowledge base."""
    try:
        results = await r2r_explorer.search(query, top_k=top_k)
        return results
    except Exception as e:
        return f"Erreur lors de la recherche : {str(e)}"

async def create_table(headers: List[str], rows: List[List[str]]) -> str:
    """Create a formatted table string."""
    tool = CreateTableTool(ToolConfig(
        name="create_table",
        description="Create a formatted table",
        category="utils"
    ))
    parameters = {
        "headers": headers,
        "rows": rows
    }
    result = await tool.execute("", parameters)
    return result

async def list_r2r_documents() -> str:
    """Liste les documents disponibles dans R2R.
    
    Returns:
        Chaîne formatée avec la liste des documents
    """
    try:
        # Utiliser la méthode list_documents de R2RExplorer
        return await r2r_explorer.list_documents()
    except Exception as e:
        return f"Erreur lors de la récupération des documents R2R : {str(e)}"

def generate_tools(args=None) -> List[LLMCompilerTool]:
    """Generate tools for LLMCompiler."""
    return [
        LLMCompilerTool(
            name="node_red_status",
            func=node_red_status,
            description=(
                "node_red_status() -> str:\n"
                " - Get the current status of Node-RED server\n"
                " - Returns status information as JSON string\n"
            ),
            stringify_rule=lambda args: "node_red_status()",
        ),
        LLMCompilerTool(
            name="get_temperature",
            func=get_temperature,
            description=(
                "get_temperature(date: Optional[str] = None, start_date: Optional[str] = None, end_date: Optional[str] = None) -> str:\n"
                " - Get temperature data for a specific date or date range\n"
                " - date: Single date in YYYY-MM-DD format\n"
                " - start_date and end_date: Date range in YYYY-MM-DD format\n"
                " - Returns temperature data as JSON string\n"
            ),
            stringify_rule=lambda args: (
                f"get_temperature("
                f"date={repr(args[0] if len(args) > 0 else None)}, "
                f"start_date={repr(args[1] if len(args) > 1 else None)}, "
                f"end_date={repr(args[2] if len(args) > 2 else None)})"
            ),
        ),
        LLMCompilerTool(
            name="get_chuck_norris_joke",
            func=get_chuck_norris_joke,
            description=(
                "get_chuck_norris_joke() -> str:\n"
                " - Get a random Chuck Norris joke\n"
                " - Returns joke as string\n"
            ),
            stringify_rule=lambda args: "get_chuck_norris_joke()",
        ),
        LLMCompilerTool(
            name="search_knowledge",
            func=search_knowledge,
            description=(
                "search_knowledge(query: str, top_k: int = 5) -> str:\n"
                " - Search for information in the R2R knowledge base\n"
                " - query: The search query\n"
                " - top_k: Number of results to return (default: 5)\n"
                " - Returns formatted search results\n"
            ),
            stringify_rule=lambda args: f"search_knowledge(query={repr(args[0])}, top_k={repr(args[1]) if len(args) > 1 else 5})",
        ),
        LLMCompilerTool(
            name="create_table",
            func=create_table,
            description=(
                "create_table(headers: List[str], rows: List[List[str]]) -> str:\n"
                " - Create a formatted table string\n"
                " - headers: List of column headers\n"
                " - rows: List of table rows\n"
                " - Returns formatted table string\n"
            ),
            stringify_rule=lambda args: f"create_table(headers={repr(args[0])}, rows={repr(args[1])})",
        ),
        LLMCompilerTool(
            name="list_r2r_documents",
            func=list_r2r_documents,
            description=(
                "list_r2r_documents() -> str:\n"
                " - List available documents in R2R\n"
                " - Returns formatted list of documents\n"
            ),
            stringify_rule=lambda args: "list_r2r_documents()",
        ),
    ]
