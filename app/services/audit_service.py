import time
from typing import Dict, Optional
from app.schemas.audit import AuditRecord

class AuditService:
    def __init__(self):
        self.traces: Dict[str, AuditRecord] = {}
        
    def create_trace(self, trace_id: str, student_id: Optional[str], question: str):
        self.traces[trace_id] = AuditRecord(
            trace_id=trace_id,
            timestamp=str(time.time()),
            student_id=student_id,
            question=question,
            final_status="started"
        )
        
    def update_trace(self, trace_id: str, updates: Dict):
        if trace_id in self.traces:
            record = self.traces[trace_id]
            for k, v in updates.items():
                if hasattr(record, k):
                    setattr(record, k, v)
                    
    def get_trace(self, trace_id: str) -> Optional[AuditRecord]:
        return self.traces.get(trace_id)

audit_service_instance = AuditService()
