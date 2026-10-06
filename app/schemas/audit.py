from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class AuditRecord(BaseModel):
    trace_id: str
    timestamp: str
    student_id: Optional[str] = None
    question: str
    route_selected: Optional[str] = None
    sources_retrieved: List[str] = []
    tools_invoked: List[str] = []
    tool_inputs: List[Dict[str, Any]] = []
    rules_applied: List[str] = []
    conflicts: List[str] = []
    answer_type: Optional[str] = None
    model_used: Optional[str] = None
    latency_ms: Optional[float] = None
    token_usage: Optional[Dict[str, int]] = None
    final_status: str
