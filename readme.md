# Red Node Pimp

A Python backend that integrates Node-RED with AI capabilities using Pydantic AI.

## Project Structure

```
red_node_pimp/
├── db/                         # Database files
│   ├── measurements.db         # SQLite database for measurements
│   ├── init_db.py             # Database initialization script
│   └── test_query.py          # Database test queries
│
├── node_red/                   # Node-RED flow management
│   ├── flows/                  # Individual flow definitions
│   │   ├── base_flow.py       # Base class for all flows
│   │   └── temperature_flow.py # Temperature measurement flow
│   ├── utils/                  # Node-RED utilities
│   │   └── node_red.py        # Deployment and management functions
│   └── deploy.py              # Main deployment script
│
└── tools/                      # AI Tools and Integrations
    ├── base_tool.py           # Base class for all tools
    ├── dependencies.py        # Shared dependencies and configurations
    ├── models.py             # Pydantic models for data validation
    └── jokes.py              # Chuck Norris jokes tool implementation
```

## Components

### Tools System

The tools system is built using Pydantic AI and follows a modular architecture:

1. **Base Tool (`tools/base_tool.py`)**
   - Abstract base class for all tools
   - Defines common interface and behaviors
   - Handles error management and logging

2. **Dependencies (`tools/dependencies.py`)**
   - Centralized dependency management
   - Environment configuration
   - Shared resources (e.g., API endpoints)

3. **Models (`tools/models.py`)**
   - Pydantic models for data validation
   - Request/Response schemas
   - Shared data structures

4. **Tool Implementations**
   - Each tool inherits from `BaseTool`
   - Example: `jokes.py` for Chuck Norris jokes
   - Follows Pydantic AI best practices

### Node-RED Integration

The Node-RED integration is organized into reusable components:

1. **Base Flow (`node_red/flows/base_flow.py`)**
   - Abstract base class for flows
   - Handles tab creation and ID management
   - Provides common flow structure

2. **Flow Implementations**
   - Each flow inherits from `NodeRedFlow`
   - Example: `temperature_flow.py` for temperature measurements
   - Self-contained flow definitions

3. **Utilities (`node_red/utils/`)**
   - Deployment management
   - Node-RED API interaction
   - Backup functionality

## Getting Started

### Prerequisites

1. **Install pyenv**
   - Windows: Follow instructions at https://github.com/pyenv-win/pyenv-win#installation
   - The project will automatically use Python 3.10 through pyenv

2. **Install Poetry**
   - Follow instructions at https://python-poetry.org/docs/#installation
   
3. **Install Node.js and npm**
   - Download and install from https://nodejs.org/
   - Install Node-RED globally: `npm install -g node-red`
   - Install SQLite node: `cd ~/.node-red && npm install node-red-node-sqlite`

### Installation

1. **Clone the project**
   ```bash
   git clone <repository-url>
   cd red_node_pimp
   ```

2. **Install dependencies**
   ```bash
   # pyenv will automatically install and use Python 3.10
   poetry install  # Install Python dependencies
   cd node_red && npm install  # Install Node-RED dependencies
   ```

3. **Deploy Node-RED flows**
   ```bash
   cd node_red
   poetry run python deploy.py  # Deploy the flows to Node-RED
   cd ..
   ```

### Starting the Application

1. **Start everything with one command**
   ```bash
   ./start_app.ps1
   ```
   This will:
   - Start Node-RED (available at http://127.0.0.1:1880)
   - Wait for Node-RED to initialize
   - Start the FastAPI server with chat interface (available at http://127.0.0.1:8000)

### Important Notes

- Node-RED must be running for temperature-related features to work
- The chat interface supports both temperature queries and Chuck Norris jokes
- All chat responses are in French, but documentation remains in English

## Creating New Components

### Adding a New Tool

1. Create a new file in `tools/`
2. Inherit from `BaseTool`
3. Define required properties:
   ```python
   class NewTool(BaseTool):
       name: str = Field("tool_name", description="...")
       description: str = Field("Tool description", ...)
   ```
4. Implement the `run` method

### Adding a New Flow

1. Create a new file in `node_red/flows/`
2. Inherit from `NodeRedFlow`
3. Implement required properties:
   ```python
   class NewFlow(NodeRedFlow):
       @property
       def name(self) -> str:
           return "Flow Name"
           
       @property
       def description(self) -> str:
           return "Flow description"
   ```
4. Add the flow to `deploy.py`

## Usage

### Tools

```python
from tools.jokes import jokes_agent

# Use the tool
result = await jokes_agent.run("Tell me a joke", deps=deps)
```

### Node-RED Flows

```bash
# Deploy all flows
python node_red/deploy.py
```

## Environment Variables

- `NODE_RED_API`: Node-RED API URL (default: "http://127.0.0.1:1880")
- `NODE_RED_API_KEY`: Optional API key for Node-RED authentication

## Development

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Initialize the database:
   ```bash
   python db/init_db.py
   ```

3. Deploy Node-RED flows:
   ```bash
   python node_red/deploy.py
   ```

4. Start the FastAPI server:
   ```bash
   uvicorn main:app --reload
   ```