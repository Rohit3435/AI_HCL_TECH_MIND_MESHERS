from langgraph.graph import StateGraph, END
from app.graph.state import GraphState
from app.graph.nodes import retrieve_node, tool_node, answer_node, refusal_node, clarification_node
from app.graph.routing import route_query
from app.services.llm_service import LLMService

llm = LLMService()

def route_router(state: GraphState):
    return state["route"]

def build_graph():
    workflow = StateGraph(GraphState)
    
    # Define Nodes
    workflow.add_node("router", lambda state: route_query(state, llm))
    workflow.add_node("retrieve", retrieve_node)
    workflow.add_node("tool", tool_node)
    workflow.add_node("answer", answer_node)
    workflow.add_node("refusal", refusal_node)
    workflow.add_node("clarification", clarification_node)
    
    # Define Edges
    workflow.set_entry_point("router")
    
    workflow.add_conditional_edges(
        "router",
        route_router,
        {
            "RAG": "retrieve",
            "TOOL": "tool",
            "RAG + TOOL": "tool",  # Route to tool first, then retrieve in a real app or vice versa
            "CLARIFICATION": "clarification",
            "REFUSAL": "refusal"
        }
    )
    
    workflow.add_edge("retrieve", "answer")
    workflow.add_edge("tool", "answer")
    
    workflow.add_edge("answer", END)
    workflow.add_edge("refusal", END)
    workflow.add_edge("clarification", END)
    
    return workflow.compile()

graph = build_graph()
