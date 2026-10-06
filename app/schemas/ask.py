from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import date, datetime

class AskRequest(BaseModel):
    question: str
    as_of_date: Optional[date] = None

class Citation(BaseModel):
    doc_id: str
    title: str
    section: Optional[str] = None
    page: Optional[int] = None
    version: Optional[str] = None
    effective_from: Optional[str] = None

class AskResponse(BaseModel):
    trace_id: str
    answer: str
    answer_type: str
    citations: List[Citation] = []
    tools_invoked: List[Dict[str, Any]] = []
    applied_rules: List[Dict[str, Any]] = []
    conflicts_detected: List[Dict[str, Any]] = []
    explanation: Optional[str] = None
    as_of_date: Optional[date] = None
