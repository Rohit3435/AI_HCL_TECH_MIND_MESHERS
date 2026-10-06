from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
async def health_check():
    return {
        "status": "ok",
        "service": "student-assistant-api",
        "llm": "available",
        "database": "available",
        "rag": "available"
    }
