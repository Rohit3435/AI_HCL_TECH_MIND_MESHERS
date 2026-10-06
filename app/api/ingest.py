import json
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.schemas.ingest import IngestResponse
from app.services.mock_services import MockIngestionService, MockSourceRegisterService
from app.schemas.source import SourceMetadata

router = APIRouter()
ingestion_service = MockIngestionService()
source_register = MockSourceRegisterService()

@router.post("/ingest", response_model=IngestResponse)
async def ingest_document(
    file: UploadFile = File(...),
    metadata: str = Form(...)
):
    try:
        metadata_dict = json.loads(metadata)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON in metadata")
        
    result = ingestion_service.ingest(file.file, metadata_dict)
    
    # Update source register if successful
    if result.status == "indexed":
        source_register.add_source(SourceMetadata(**metadata_dict))
        
    return result
