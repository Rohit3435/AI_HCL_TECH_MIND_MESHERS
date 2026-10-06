from typing import Protocol, List, Dict, Any, Optional
from pydantic import BaseModel

class RetrievedDocument(BaseModel):
    doc_id: str
    title: str
    section: Optional[str] = None
    page: Optional[int] = None
    version: Optional[str] = None
    effective_from: Optional[str] = None
    effective_to: Optional[str] = None
    score: float
    content: str

class RAGServiceInterface(Protocol):
    def search(self, query: str, top_k: int = 5, filters: Optional[Dict[str, Any]] = None) -> List[RetrievedDocument]:
        ...
