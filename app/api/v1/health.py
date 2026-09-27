from fastapi import APIRouter
from app.schemas.common import APIResponse

router = APIRouter()

@router.get("", response_model=APIResponse[dict])
async def health_check():
    return APIResponse(
        success=True,
        message="AetherMind Multimodal AI Unified Platform Operational",
        data={"status": "healthy", "version": "3.0.0"}
    )
