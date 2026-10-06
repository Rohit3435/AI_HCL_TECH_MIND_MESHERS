from typing import TypedDict, List, Dict, Any, Optional
from datetime import date

class GraphState(TypedDict):
    trace_id: str
    student_id: Optional[str]
    question: str
    as_of_date: date
    intent: Optional[str]
    entities: Dict[str, Any]
    route: Optional[str]
    retrieved_context: List[Any]
    tool_results: List[Any]
    citations: List[Any]
    rules_applied: List[str]
    conflicts_detected: List[str]
    answer: Optional[str]
    answer_type: Optional[str]
    explanation: Optional[str]
    errors: List[str]
