from fastapi import APIRouter
from app.schemas.common import APIResponse

router = APIRouter()

@router.get("", response_model=APIResponse[dict])
async def settings_blueprint():
    return APIResponse(success=True, message="Settings blueprint", data={})
