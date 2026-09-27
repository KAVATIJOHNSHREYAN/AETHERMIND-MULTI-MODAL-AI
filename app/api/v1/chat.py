from fastapi import APIRouter
from app.schemas.common import APIResponse

router = APIRouter()

@router.get("", response_model=APIResponse[list])
async def list_chats():
    return APIResponse(success=True, data=[], message="Chats blueprint")
