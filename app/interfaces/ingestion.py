from typing import Protocol, Dict, Any, BinaryIO
from app.schemas.ingest import IngestResponse

class DocumentIngestionServiceInterface(Protocol):
    def ingest(self, file: BinaryIO, metadata: Dict[str, Any]) -> IngestResponse:
        ...
