from fastapi import APIRouter, HTTPException
from app.schemas.audit import AuditRecord
from app.services.audit_service import audit_service_instance

router = APIRouter()

@router.get("/audit/{trace_id}", response_model=AuditRecord)
async def get_audit(trace_id: str):
    trace = audit_service_instance.get_trace(trace_id)
    if not trace:
        raise HTTPException(status_code=404, detail="Trace not found")
    return trace
