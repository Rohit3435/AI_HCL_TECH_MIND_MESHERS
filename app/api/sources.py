from fastapi import APIRouter
from app.schemas.source import SourcesResponse
from app.services.mock_services import MockSourceRegisterService

router = APIRouter()
source_register = MockSourceRegisterService()

@router.get("/sources", response_model=SourcesResponse)
async def get_sources():
    sources = source_register.get_all_sources()
    return SourcesResponse(sources=sources)
