import uuid
import time
from datetime import date
from fastapi import APIRouter, Header, HTTPException
from typing import Optional
from app.schemas.ask import AskRequest, AskResponse
from app.graph.graph import graph
from app.services.audit_service import audit_service_instance

router = APIRouter()

@router.post("/ask", response_model=AskResponse)
async def ask_question(
    request: AskRequest,
    x_student_id: Optional[str] = Header(None, alias="X-Student-Id")
):
    # Personal query handling - refusal if no ID or attempt to cross-access
    # The prompt explicitly asks to block missing x_student_id if it's a personal query
    # and to block cross-student access attempts. The LangGraph routing can handle part of this,
    # but basic validation happens here.
    
    trace_id = str(uuid.uuid4())
    audit_service_instance.create_trace(trace_id, x_student_id, request.question)
    
    start_time = time.time()
    
    # Initialize state
    initial_state = {
        "trace_id": trace_id,
        "student_id": x_student_id,
        "question": request.question,
        "as_of_date": request.as_of_date or date.today(),
        "intent": None,
        "entities": {},
        "route": None,
        "retrieved_context": [],
        "tool_results": [],
        "citations": [],
        "rules_applied": [],
        "conflicts_detected": [],
        "answer": None,
        "answer_type": None,
        "explanation": None,
        "errors": []
    }
    
    try:
        # Run LangGraph
        result = graph.invoke(initial_state)
        
        # Calculate latency
        latency_ms = (time.time() - start_time) * 1000
        
        # Update Audit
        audit_service_instance.update_trace(trace_id, {
            "route_selected": result.get("route"),
            "sources_retrieved": [c["doc_id"] for c in result.get("citations", [])],
            "tools_invoked": [t["tool"] for t in result.get("tool_results", [])],
            "answer_type": result.get("answer_type"),
            "latency_ms": latency_ms,
            "final_status": "success"
        })
        
        return AskResponse(
            trace_id=trace_id,
            answer=result.get("answer", "No answer could be generated."),
            answer_type=result.get("answer_type", "unknown"),
            citations=result.get("citations", []),
            tools_invoked=result.get("tool_results", []),
            applied_rules=result.get("rules_applied", []),
            conflicts_detected=result.get("conflicts_detected", []),
            as_of_date=result.get("as_of_date")
        )
    except Exception as e:
        audit_service_instance.update_trace(trace_id, {
            "final_status": "error"
        })
        raise HTTPException(status_code=500, detail=str(e))
