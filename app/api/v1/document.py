from fastapi import APIRouter
from app.schemas.common import APIResponse

router = APIRouter()

@router.get("", response_model=APIResponse[dict])
async def document_blueprint():
    return APIResponse(success=True, message="Document blueprint", data={})
