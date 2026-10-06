from app.graph.routing import route_query
from app.services.llm_service import LLMService

def test_route_tool_only():
    state = {"question": "What is my attendance in CS201?"}
    llm = LLMService() # mock
    updated = route_query(state, llm)
    assert updated["route"] == "TOOL"

def test_route_rag_only():
    state = {"question": "What are the university policy on minimum attendance?"}
    llm = LLMService()
    updated = route_query(state, llm)
    assert updated["route"] == "RAG"

def test_route_refusal():
    state = {"question": "What is s1002's attendance?"}
    llm = LLMService()
    updated = route_query(state, llm)
    assert updated["route"] == "REFUSAL"
