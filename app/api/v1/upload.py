from fastapi import APIRouter
from app.schemas.common import APIResponse

router = APIRouter()

@router.post("", response_model=APIResponse[dict])
async def upload_blueprint():
    return APIResponse(success=True, message="Upload blueprint", data={})
