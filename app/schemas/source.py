from pydantic import BaseModel
from typing import Optional, List

class SourceMetadata(BaseModel):
    doc_id: str
    title: str
    issuer: Optional[str] = None
    authority_level: Optional[int] = None
    doc_type: Optional[str] = None
    version: Optional[str] = None
    effective_from: Optional[str] = None
    effective_to: Optional[str] = None
    supersedes: List[str] = []
    scope_programmes: Optional[str] = "all"
    scope_batches: Optional[str] = "all"
    source_url: Optional[str] = None
    retrieved_on: Optional[str] = None
    synthetic: str = "false"

class SourcesResponse(BaseModel):
    sources: List[SourceMetadata]
