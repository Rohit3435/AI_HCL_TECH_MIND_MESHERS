from app.graph.state import GraphState
from app.services.llm_service import LLMService

def route_query(state: GraphState, llm: LLMService) -> GraphState:
    question = state["question"].lower()
    
    # Simple deterministic heuristic for routing
    if "attendance" in question and "my" in question:
        state["route"] = "TOOL"
        state["intent"] = "get_attendance"
    elif "policy" in question or "rules" in question or "minimum" in question:
        state["route"] = "RAG"
    elif "eligible" in question:
        state["route"] = "RAG + TOOL"
        state["intent"] = "check_eligibility"
    elif "s100" in question and "my" not in question:
        # Very basic check for cross-student access attempts
        state["route"] = "REFUSAL"
    else:
        # Fallback to LLM based routing
        schema = {
            "type": "object",
            "properties": {
                "route": {"type": "string", "enum": ["RAG", "TOOL", "RAG + TOOL", "CLARIFICATION", "REFUSAL"]},
                "intent": {"type": "string"}
            },
            "required": ["route"]
        }
        prompt = f"Analyze the following student question and determine the route. Question: {question}"
        res = llm.structured(prompt, schema)
        state["route"] = res.get("route", "CLARIFICATION")
        state["intent"] = res.get("intent", "unknown")
        
    return state
