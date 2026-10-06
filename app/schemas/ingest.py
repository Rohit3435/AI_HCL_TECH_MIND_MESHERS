from pydantic import BaseModel
from typing import Optional, List

class IngestResponse(BaseModel):
    doc_id: str
    chunks_indexed: int
    status: str
