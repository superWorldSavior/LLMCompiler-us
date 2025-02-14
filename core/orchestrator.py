"""Orchestrator for the agent."""
from typing import Dict, Any, List
from loguru import logger
from langgraph.prebuilt import ToolExecutor
from langgraph.graph import StateGraph, END

from core.llm_manager import LLMManager
from tools.tools_manager import ToolsManager
from core.base_orchestrator import (
    PlanExecute,
    Plan,
    ChatRequest,
    ChatResponse,
    Message
)

class Orchestrator:
    """Orchestrator for the agent."""
    
    def __init__(self, llm_manager: LLMManager, tools_manager: ToolsManager):
        """Initialize the orchestrator.
        
        Args:
            llm_manager: LLM manager
            tools_manager: Tools manager
        """
        self.llm_manager = llm_manager
        self.tools_manager = tools_manager
        self.workflow = self._create_workflow()
        logger.debug("Orchestrator initialized")
        
    def _create_workflow(self) -> StateGraph:
        """Create the agent workflow graph."""
        logger.debug("Creating workflow graph")
        
        # Create graph
        workflow = StateGraph(PlanExecute)
        logger.debug("Graph instance created")
        
        # Define node functions
        async def plan(state: Dict) -> Dict:
            """Create a plan."""
            logger.info("Plan step", state=state)
            logger.debug("Planning input", input=state["input"])
            
            # Get plan from LLM
            plan = await self.llm_manager.plan(state["input"])
            logger.debug("Got plan from LLM", plan=plan)
            
            # Initialize state if needed
            if "steps" not in state:
                state["steps"] = []
            if "past_steps" not in state:
                state["past_steps"] = []
            if "needs_replan" not in state:
                state["needs_replan"] = False
            if "response" not in state:
                state["response"] = ""
            
            # Add steps from plan
            state["steps"].extend(plan["steps"])
            logger.debug("Updated state", state=state)
            
            return state

        async def execute(state: Dict) -> Dict:
            """Execute a step from the plan."""
            logger.info("Execute step", state=state)
            
            # Vérifier qu'on a des steps
            if not state.get("steps"):
                logger.warning("No steps available to execute", state=state)
                return {
                    **state,
                    "response": "Je ne sais pas comment répondre à cette requête. Pouvez-vous reformuler ou être plus précis ?"
                }
            
            current_step = state["steps"][0]
            logger.debug("Current step", step=current_step)
            
            # Si c'est une demande d'info à l'utilisateur
            if current_step.startswith("ASK_USER:"):
                question = current_step[9:].strip()
                logger.info("Asking user", question=question)
                return {
                    **state,
                    "response": question,
                    "needs_replan": True
                }
            
            # Sinon exécuter le step normalement
            response = await self.llm_manager.execute(state)
            logger.debug("Got response from LLM", response=response)
            
            # Si on doit replanifier
            if response.get("needs_replan"):
                return {**state, "response": response["response"], "needs_replan": True}
                
            # Update state
            new_state = {
                **state,
                **response,
                "steps": state["steps"][1:],  # Remove executed step
                "past_steps": state.get("past_steps", []) + [state["steps"][0]]  # Add to past steps
            }
            logger.debug("State updated", 
                        remaining_steps=len(new_state["steps"]),
                        past_steps=len(new_state["past_steps"]))
            
            return new_state

        async def check(state: Dict) -> Dict:
            """Check if we need to continue executing steps."""
            logger.info("Check step", state=state)
            logger.debug("Checking state", 
                        has_steps=bool(state.get("steps")),
                        step_count=len(state.get("steps", [])),
                        past_steps=len(state.get("past_steps", [])))
            return state
        
        def should_end(state: Dict) -> bool:
            """Decide if we should end."""
            should_stop = not state.get("steps") or state.get("needs_replan")
            logger.debug("Checking end condition", should_end=should_stop, state=state)
            return should_stop
        
        # Add nodes
        logger.debug("Adding nodes to graph")
        workflow.add_node("planner", plan)
        workflow.add_node("executor", execute)
        workflow.add_node("checker", check)
        
        # Set entry point
        workflow.set_entry_point("planner")
        
        # Add edges
        logger.debug("Adding edges to graph")
        workflow.add_conditional_edges(
            "checker",
            should_end,
            {
                True: END,
                False: "executor"
            }
        )
        workflow.add_edge("executor", "checker")
        workflow.add_edge("planner", "executor")
        
        # Compile the workflow
        logger.debug("Compiling workflow")
        return workflow.compile()
        
    async def process_request(self, request: ChatRequest) -> ChatResponse:
        """Process a chat request."""
        try:
            logger.info("Processing request", message=request["message"])
            
            # Create initial state
            state = {
                "input": request["message"],
                "steps": [],
                "past_steps": [],
                "response": "",
                "needs_replan": False
            }
            
            # Run workflow
            final_state = await self.workflow.ainvoke(state)
            logger.debug("Final state", state=final_state)
            
            # Format response
            response = final_state.get("response", "")
            if isinstance(response, dict):
                if "content" not in response:
                    raise ValueError("Response dict must have 'content' key")
                response = response["content"]
            elif not isinstance(response, str):
                raise ValueError(f"Response must be string or dict with 'content', got {type(response)}")
            
            return {
                "response": response,
                "message_history": [{
                    "role": "user",
                    "content": request["message"]
                }, {
                    "role": "assistant",
                    "content": response
                }]
            }
                
        except Exception as e:
            logger.exception("Error processing request")
            return {
                "response": f"Une erreur est survenue: {str(e)}",
                "message_history": [{
                    "role": "assistant",
                    "content": f"Erreur: {str(e)}"
                }]
            }
