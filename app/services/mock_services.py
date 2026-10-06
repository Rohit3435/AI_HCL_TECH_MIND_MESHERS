import uuid
from typing import List, Dict, Any, Optional, BinaryIO
from datetime import datetime, timezone

from app.interfaces.rag import RAGServiceInterface, RetrievedDocument
from app.interfaces.tools import ToolRegistryInterface
from app.interfaces.student_repository import StudentRepositoryInterface
from app.interfaces.ingestion import DocumentIngestionServiceInterface
from app.interfaces.source_register import SourceRegisterServiceInterface
from app.schemas.ingest import IngestResponse
from app.schemas.source import SourceMetadata

class MockRAGService(RAGServiceInterface):
    def search(self, query: str, top_k: int = 5, filters: Optional[Dict[str, Any]] = None) -> List[RetrievedDocument]:
        return [
            RetrievedDocument(
                doc_id="MOCK-REG-01",
                title="Mock Academic Regulations",
                section="Attendance",
                page=1,
                version="1.0",
                score=0.95,
                content="Students must maintain 75% attendance to be eligible for exams."
            )
        ]

class MockToolRegistry(ToolRegistryInterface):
    def execute(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        if tool_name == "get_attendance":
            return {"course": arguments.get("course_code"), "attendance": "80%"}
        return {"error": "Tool not found"}
    
    def has_tool(self, tool_name: str) -> bool:
        return tool_name in ["get_attendance", "get_results", "check_exam_eligibility"]

class MockStudentRepository(StudentRepositoryInterface):
    def __init__(self):
        self.db = {
            "S1001": {"name": "Alice", "program": "CS"},
            "S1002": {"name": "Bob", "program": "EE"}
        }

    def get_student(self, student_id: str) -> Optional[Dict[str, Any]]:
        return self.db.get(student_id)
    
    def upsert_student(self, student_id: str, data: Dict[str, Any]) -> None:
        self.db[student_id] = data

class MockIngestionService(DocumentIngestionServiceInterface):
    def ingest(self, file: BinaryIO, metadata: Dict[str, Any]) -> IngestResponse:
        return IngestResponse(
            doc_id=metadata.get("doc_id", str(uuid.uuid4())),
            chunks_indexed=10,
            status="indexed"
        )

class MockSourceRegisterService(SourceRegisterServiceInterface):
    def __init__(self):
        self.sources = [
            SourceMetadata(
                doc_id="MOCK-REG-01",
                title="Mock Academic Regulations",
                retrieved_on=datetime.now(timezone.utc).isoformat()
            )
        ]

    def get_all_sources(self) -> List[SourceMetadata]:
        return self.sources
    
    def add_source(self, source: SourceMetadata) -> None:
        self.sources.append(source)
