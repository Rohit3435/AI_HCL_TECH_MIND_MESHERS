from typing import Protocol, Optional, Dict, Any

class StudentRepositoryInterface(Protocol):
    def get_student(self, student_id: str) -> Optional[Dict[str, Any]]:
        ...
    
    def upsert_student(self, student_id: str, data: Dict[str, Any]) -> None:
        ...
