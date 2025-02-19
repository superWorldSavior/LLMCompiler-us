"""ITTPC prompts."""
from langchain.prompts.prompt import PromptTemplate
from llmcompiler.src.llm_compiler.constants import END_OF_PLAN, JOINNER_FINISH, JOINNER_REPLAN

EXAMPLE = (
    "Question: Show temperatures for 2023-01-01 to 2023-01-03\n\n"
    "Thought: I need to check if Node-RED is operational first\n"
    "1. NodeStatus[]\n"
    "Observation: Node-RED is operational\n\n"
    "Thought: Let me check if these dates are available in Node-RED\n"
    "2. TemperatureRange[2023-01-01, 2023-01-03]\n"
    "Observation: Error: Temperatures not available for this date range. Available range: 2024-01-01 to 2024-02-18\n\n"
    "Thought: The requested dates are not available. I should inform the user and show the available range instead.\n"
    "Action: Replan(Dates not available, showing most recent data instead)\n\n"
    "Thought: Let me get the last 3 days of available data instead\n"
    "1. TemperatureRange[2024-02-16, 2024-02-18]\n"
    "Observation: {\"2024-02-16\": 22.5, \"2024-02-17\": 23.1, \"2024-02-18\": 21.8}\n\n"
    "Thought: Now I can format this data as a table\n"
    "2. Table[[\"Date\", \"Temperature (°C)\"], [[\"2024-02-16\", \"22.5\"], [\"2024-02-17\", \"23.1\"], [\"2024-02-18\", \"21.8\"]]]\n"
    "Observation: Table: headers=Date,Temperature (°C)|2024-02-16,22.5|2024-02-17,23.1|2024-02-18,21.8\n\n"
    "Thought: I have the alternative data to show\n"
    f"3. join()\n{END_OF_PLAN}\n\n"
)

PREFIX = (
    "Solve a task with interleaving Thought, Action, Observation steps. "
    "Thought can reason about the current situation. "
    "After Thought, you MUST always take an Action.\n\n"
    "Action can be one of these types:\n"
    "  (1) NodeStatus[]: Check Node-RED server status\n"
    "  (2) Temperature[date]: Get temperature for a specific date (YYYY-MM-DD)\n"
    "  (3) TemperatureRange[start_date, end_date]: Get temperature for a date range\n"
    "  (4) Search[query]: Search in R2R knowledge base\n"
    "  (5) Joke[]: Get a random Chuck Norris joke\n"
    "  (6) Table[[\"col1\", \"col2\"], [[\"row1val1\", \"row1val2\"], [\"row2val1\", \"row2val2\"]]]: Create a formatted table\n"
    "  (7) join(): Return the answer and finish the task\n\n"
    "Guidelines:\n"
    "  - Each action MUST be in the format: <action_id>. <action_name>[<args>]\n"
    "  - Action IDs MUST start at 1 and increment by 1\n"
    "  - You MUST use join() as the last action\n"
    "  - Always check Node-RED status before accessing temperature data\n"
    "  - Temperature and TemperatureRange actions can only be used after NodeStatus confirms operational\n"
    "  - Table action should only be used after having all required data\n"
    "  - If requested temperatures are not available:\n"
    "    1. Check the error message for available date range\n"
    "    2. Use Replan to show data from available dates instead\n"
    "    3. In the new plan, use dates that are confirmed to be available\n"
    "  - Format dates as YYYY-MM-DD\n"
    "  - For tabular data:\n"
    "    - Use Table[headers, rows]\n"
    "    - Include units in headers\n"
    "    - Round numbers to 1 decimal\n"
    "  - Never show raw observations in final answer\n"
    "  - Never search for the same query twice\n"
    "  - Never introduce new Action types\n\n"
    "Example:\n\n"
)

SYSTEM_PROMPT = (
    "You are an AI assistant helping to solve a task. "
    "You can use the following actions:\n\n"
    "  (1) Search[query]: Search in R2R knowledge base\n"
    "  (2) Joke[]: Get a random Chuck Norris joke\n"
    "  (3) Table[[\"col1\", \"col2\"], [[\"row1val1\", \"row1val2\"], [\"row2val1\", \"row2val2\"]]]: Create a formatted table\n"
    "  (4) list_r2r_documents[]: List all available documents in R2R knowledge base\n"
    "  (5) join(): Return the answer and finish the task\n\n"
    "Guidelines:\n"
    "  - Each action MUST be in the format: <action_id>. <action_name>[<args>]\n"
    "  - Action IDs MUST start at 1 and increment by 1\n"
    "  - Each action MUST be on a new line\n"
    "  - Each action MUST be followed by its output on the next line\n"
    "  - You MUST wait for an action's output before proceeding\n"
    "  - You MUST join() when you have the answer\n\n"
    "Example:\n"
    "1. Search[\"What is the capital of France?\"]\n"
    "Paris is the capital of France\n"
    "2. join()\n"
    "Based on the search results, Paris is the capital of France.\n\n"
    "Begin helping with the task!"
)

SUFFIX = (
    "Question: {input}\n"
    "{agent_scratchpad}"
)

PLANNER_PROMPT = PREFIX + EXAMPLE + SUFFIX

OUTPUT_PROMPT = (
    "Répondez à la question en suivant ces directives :\n"
    "1. Soyez concis et naturel\n"
    "2. Utilisez des emojis appropriés\n"
    "3. Ne montrez jamais les données brutes (JSON, status codes)\n"
    "4. Pour les températures :\n"
    "   - Indiquez la date et l'unité (°C)\n"
    "   - Arrondissez à 1 décimale\n"
    "   - Si les dates demandées ne sont pas disponibles :\n"
    "     * Expliquez quelles dates sont disponibles\n"
    "     * Montrez les données les plus pertinentes disponibles\n"
    "5. Pour Node-RED :\n"
    "   - Dites simplement s'il est opérationnel\n"
    "6. Pour les blagues :\n"
    "   - Ajoutez un emoji 😄\n"
    "7. Pour les données tabulaires :\n"
    "   - Utilisez le format Table: headers=column1,column2,column3|row1value1,row1value2,row1value3|row2value1,row2value2,row2value3\n"
    f"{JOINNER_FINISH}\n"
)

PROMPT = PromptTemplate(
    template=PLANNER_PROMPT + "\n###\n" + OUTPUT_PROMPT,
    input_variables=["input", "agent_scratchpad"]
)
