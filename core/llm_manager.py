"""LLM manager for the agent."""
from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from loguru import logger
import json

class LLMManager:
    """LLM manager for the agent."""
    
    def __init__(self, tools_manager):
        """Initialize the LLM manager."""
        self.tools_manager = tools_manager
        self.llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0)
        logger.debug("LLM Manager initialized")
        
        # Get tools description
        self.available_tools = self.tools_manager.list_tools()
        tools_desc = "\n".join([
            f"- {tool['name']}: {tool['description']}"
            for tool in self.available_tools
        ])
        logger.debug("Tools description", desc=tools_desc)
        
        # Simple prompts
        self.planner_prompt = ChatPromptTemplate.from_messages([
            ("system", f"""Tu es un assistant qui crée des plans étape par étape.
Pour chaque requête, retourne une liste d'étapes, une par ligne.

Tu as accès à ces outils:
{tools_desc}

Format des réponses:
ASK_USER: <question>  # Pour demander des infos
USE_TOOL: <outil> <params>  # Pour utiliser un outil 
Répondre directement: <réponse>  # Pour répondre sans outil

Retourne TOUJOURS au moins une ligne."""),
            ("human", "{input}")
        ])
        
        self.executor_prompt = ChatPromptTemplate.from_messages([
            ("system", "Tu es un assistant qui répond en français."),
            ("human", "{task}")
        ])
        
    async def plan(self, input: str) -> Dict[str, List[str]]:
        """Plan steps to execute."""
        logger.info("Planning steps", input=input)
        
        # Format prompt
        messages = self.planner_prompt.format_messages(input=input)
        logger.debug("Formatted prompt", messages=messages)
        
        # Get plan from LLM
        response = await self.llm.ainvoke(messages)
        logger.debug("LLM response", content=response.content)
        
        # Parse steps
        steps = [s.strip() for s in response.content.split('\n') if s.strip()]
        logger.debug("Parsed steps", steps=steps, step_count=len(steps))
        
        if not steps:
            logger.warning("No steps found, using response as direct response")
            steps = ["Répondre directement: " + response.content]
            
        result = {"steps": steps}
        logger.debug("Final plan", plan=result, step_count=len(steps), steps=steps)
        return result

    def _get_tool_params(self, tool_name: str) -> str:
        """Get tool parameters description."""
        tool = self.tools_manager.get_tool(tool_name)
        params = []
        for param in tool.config["required_parameters"]:
            required = "requis" if param["required"] else "optionnel"
            params.append(f"- {param['name']}: {param['description']} ({required})")
        return "\n  ".join(params) if params else "Aucun paramètre requis"
    
    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the current step."""
        current_step = state["steps"][0]
        logger.info("LLM execution started", step=current_step)
        logger.debug("Creating execution chain")
        
        # Si c'est une réponse directe, on extrait juste la réponse
        if current_step.startswith("Répondre directement: "):
            response_text = current_step[len("Répondre directement: "):]
            return {"response": response_text}
            
        # Si c'est une demande à l'utilisateur
        if current_step.startswith("ASK_USER: "):
            question = current_step[len("ASK_USER: "):]
            return {
                "response": question,
                "needs_replan": True
            }
            
        # Si c'est une utilisation d'outil
        if current_step.startswith("USE_TOOL: "):
            try:
                # Parse tool name and params
                tool_line = current_step[len("USE_TOOL: "):]
                tool_name = tool_line.split(" ")[0]
                params_json = tool_line[len(tool_name):].strip()
                params = json.loads(params_json)
                
                # Get tool and check required parameters
                tool = self.tools_manager.get_tool(tool_name)
                missing_params = []
                for param in tool.config["required_parameters"]:
                    if param["required"] and param["name"] not in params:
                        missing_params.append(param)
                
                # If missing parameters, ask user and replan
                if missing_params:
                    param_desc = "\n".join([f"- {p['name']}: {p['description']}" for p in missing_params])
                    return {
                        "response": f"J'ai besoin des informations suivantes pour utiliser l'outil {tool_name}:\n{param_desc}\nVeuillez me fournir ces informations.",
                        "needs_replan": True
                    }
                
                # Execute tool
                result = await tool.execute(**params)
                return {"response": f"Résultat de {tool_name}: {result}"}
                
            except Exception as e:
                logger.exception(f"Error executing tool {tool_name}")
                return {"response": f"Erreur lors de l'exécution de l'outil {tool_name}: {str(e)}"}
            
        # Sinon on exécute normalement le step avec le LLM
        response = await self.llm.ainvoke(current_step)
        logger.debug("Raw LLM response", response=response)
        
        return {"response": response.content}
