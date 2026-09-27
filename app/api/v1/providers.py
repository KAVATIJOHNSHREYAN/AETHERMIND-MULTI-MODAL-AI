from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.schemas.common import APIResponse
from app.core.dependencies import get_db, get_current_user
from app.models.user import User
from app.models.provider import AIProviderConfig
from app.security.key_manager import APIKeyManager
from app.providers.manager import ai_provider_manager
from app.providers.registry import provider_registry
import uuid

router = APIRouter()

class SaveProviderKeyRequest(BaseModel):
    provider_name: str
    api_key: str
    api_base_url: Optional[str] = None
    is_enabled: Optional[bool] = True

class TestProviderRequest(BaseModel):
    provider_name: str
    api_key: str

class DispatchAIRequest(BaseModel):
    model: str = "gemini-2.5-flash"
    messages: List[Dict[str, Any]]

@router.get("", response_model=APIResponse[list])
async def list_providers():
    """List all 12 supported AI providers and model registries"""
    providers = provider_registry.list_all_providers()
    return APIResponse(success=True, message="Providers retrieved", data=providers)

@router.post("/keys", response_model=APIResponse[dict])
async def save_provider_key(
    payload: SaveProviderKeyRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Save encrypted API key for a specified AI provider"""
    encrypted_key = APIKeyManager.encrypt_key(payload.api_key)
    
    result = await db.execute(
        select(AIProviderConfig).filter(
            AIProviderConfig.user_id == current_user.id,
            AIProviderConfig.provider_name == payload.provider_name
        )
    )
    config_obj = result.scalars().first()

    if not config_obj:
        config_obj = AIProviderConfig(
            id=str(uuid.uuid4()),
            user_id=current_user.id,
            provider_name=payload.provider_name,
            api_key_encrypted=encrypted_key,
            api_base_url=payload.api_base_url,
            is_enabled=payload.is_enabled,
        )
        db.add(config_obj)
    else:
        config_obj.api_key_encrypted = encrypted_key
        config_obj.is_enabled = payload.is_enabled
        if payload.api_base_url:
            config_obj.api_base_url = payload.api_base_url

    await db.commit()
    await db.refresh(config_obj)

    return APIResponse(
        success=True,
        message=f"Encrypted API key for provider [{payload.provider_name}] saved successfully",
        data={
            "provider_name": payload.provider_name,
            "masked_key": APIKeyManager.mask_key(payload.api_key),
            "is_enabled": config_obj.is_enabled
        }
    )

@router.post("/test", response_model=APIResponse[dict])
async def test_provider_connection(payload: TestProviderRequest):
    """Test connectivity and API key validity for a provider"""
    result = await ai_provider_manager.test_provider_connection(payload.provider_name, payload.api_key)
    return APIResponse(
        success=result["success"],
        message="Provider test complete",
        data=result
    )

@router.post("/dispatch", response_model=APIResponse[dict])
async def dispatch_ai_request(payload: DispatchAIRequest):
    """Central AI Request Dispatcher endpoint"""
    response_text = await ai_provider_manager.generate(
        model=payload.model,
        messages=payload.messages
    )
    return APIResponse(
        success=True,
        message="AI request dispatched successfully",
        data={"model": payload.model, "response": response_text}
    )
