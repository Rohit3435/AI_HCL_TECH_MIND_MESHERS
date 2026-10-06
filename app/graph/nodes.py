from app.graph.state import GraphState
from app.services.mock_services import MockRAGService, MockToolRegistry
from app.services.llm_service import LLMService

rag_service = MockRAGService()
tool_registry = MockToolRegistry()
llm = LLMService()

def retrieve_node(state: GraphState) -> GraphState:
    docs = rag_service.search(state["question"])
    state["retrieved_context"] = [{"doc_id": d.doc_id, "content": d.content} for d in docs]
    state["citations"] = [{"doc_id": d.doc_id, "title": d.title} for d in docs]
    return state

def tool_node(state: GraphState) -> GraphState:
    # Just a basic extraction for mock purposes
    if state["intent"] == "get_attendance":
        res = tool_registry.execute("get_attendance", {"course_code": "CS201"})
        state["tool_results"].append({"tool": "get_attendance", "result": res})
    return state

def answer_node(state: GraphState) -> GraphState:
    context = state.get("retrieved_context", [])
    tools = state.get("tool_results", [])
    
    prompt = f"Answer the question: '{state['question']}' using this context: {context} and tool results: {tools}"
    answer = llm.generate(prompt)
    
    state["answer"] = answer
    state["answer_type"] = "calculated" if tools else "retrieved_fact"
    return state

def refusal_node(state: GraphState) -> GraphState:
    state["answer"] = "I cannot fulfill this request due to privacy or policy restrictions."
    state["answer_type"] = "refused"
    return state

def clarification_node(state: GraphState) -> GraphState:
    state["answer"] = "Could you please clarify your request? I need more details to assist you."
    state["answer_type"] = "clarification_needed"
    return state
