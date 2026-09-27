from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File as FastAPIFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.schemas.common import APIResponse
from app.schemas.auth import UserProfileResponse, UserProfileUpdate, UserSettingsUpdate
from app.core.dependencies import get_db, get_current_user
from app.models.user import User
from app.models.settings import UserSettings
from app.models.auth_metadata import AuthMetadata
import os

router = APIRouter()

@router.get("/me", response_model=APIResponse[UserProfileResponse])
async def get_my_profile(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Retrieve profile details for currently authenticated user"""
    meta_res = await db.execute(select(AuthMetadata).filter(AuthMetadata.user_id == current_user.id))
    meta = meta_res.scalars().first()

    profile_dict = {
        "id": current_user.id,
        "clerk_id": current_user.clerk_id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "avatar_url": current_user.avatar_url,
        "provider_type": current_user.provider_type,
        "role": current_user.role,
        "is_active": current_user.is_active,
        "is_verified": current_user.is_verified,
        "is_admin": current_user.is_admin,
        "created_at": current_user.created_at,
        "last_login_at": meta.last_login_at if meta else None,
    }

    return APIResponse(
        success=True,
        message="Profile retrieved successfully",
        data=UserProfileResponse.model_validate(profile_dict)
    )

@router.patch("/me", response_model=APIResponse[UserProfileResponse])
async def update_my_profile(
    payload: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update user profile details (Full Name, Avatar URL)"""
    if payload.full_name is not None:
        current_user.full_name = payload.full_name
    if payload.avatar_url is not None:
        current_user.avatar_url = payload.avatar_url

    db.add(current_user)
    await db.commit()
    await db.refresh(current_user)

    meta_res = await db.execute(select(AuthMetadata).filter(AuthMetadata.user_id == current_user.id))
    meta = meta_res.scalars().first()

    profile_dict = {
        "id": current_user.id,
        "clerk_id": current_user.clerk_id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "avatar_url": current_user.avatar_url,
        "provider_type": current_user.provider_type,
        "role": current_user.role,
        "is_active": current_user.is_active,
        "is_verified": current_user.is_verified,
        "is_admin": current_user.is_admin,
        "created_at": current_user.created_at,
        "last_login_at": meta.last_login_at if meta else None,
    }

    return APIResponse(
        success=True,
        message="Profile updated successfully",
        data=UserProfileResponse.model_validate(profile_dict)
    )

@router.get("/settings", response_model=APIResponse[dict])
async def get_user_settings(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Retrieve settings & preferences for currently authenticated user"""
    result = await db.execute(select(UserSettings).filter(UserSettings.user_id == current_user.id))
    settings_obj = result.scalars().first()
    if not settings_obj:
        settings_obj = UserSettings(user_id=current_user.id)
        db.add(settings_obj)
        await db.commit()
        await db.refresh(settings_obj)

    return APIResponse(
        success=True,
        message="User settings retrieved",
        data={
            "theme": settings_obj.theme,
            "default_model": settings_obj.default_model,
            "enable_memory": settings_obj.enable_memory,
            "enable_search": settings_obj.enable_search,
            "voice_accent": settings_obj.voice_accent,
            "custom_instructions": settings_obj.custom_instructions,
        }
    )

@router.put("/settings", response_model=APIResponse[dict])
async def update_user_settings(
    payload: UserSettingsUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update settings & preferences for currently authenticated user"""
    result = await db.execute(select(UserSettings).filter(UserSettings.user_id == current_user.id))
    settings_obj = result.scalars().first()
    if not settings_obj:
        settings_obj = UserSettings(user_id=current_user.id)
        db.add(settings_obj)

    if payload.theme is not None:
        settings_obj.theme = payload.theme
    if payload.default_model is not None:
        settings_obj.default_model = payload.default_model
    if payload.voice_accent is not None:
        settings_obj.voice_accent = payload.voice_accent
    if payload.custom_instructions is not None:
        settings_obj.custom_instructions = payload.custom_instructions

    db.add(settings_obj)
    await db.commit()
    await db.refresh(settings_obj)

    return APIResponse(
        success=True,
        message="User settings updated successfully",
        data={
            "theme": settings_obj.theme,
            "default_model": settings_obj.default_model,
            "enable_memory": settings_obj.enable_memory,
            "enable_search": settings_obj.enable_search,
            "voice_accent": settings_obj.voice_accent,
            "custom_instructions": settings_obj.custom_instructions,
        }
    )

@router.post("/avatar", response_model=APIResponse[dict])
async def upload_avatar(
    file: UploadFile = FastAPIFile(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Upload user avatar image file"""
    static_avatars_dir = os.path.join("app", "static", "uploads", "avatars")
    os.makedirs(static_avatars_dir, exist_ok=True)
    
    file_ext = os.path.splitext(file.filename)[1] if file.filename else ".png"
    filename = f"avatar_{current_user.id}{file_ext}"
    filepath = os.path.join(static_avatars_dir, filename)

    contents = await file.read()
    with open(filepath, "wb") as f:
        f.write(contents)

    avatar_url = f"/static/uploads/avatars/{filename}"
    current_user.avatar_url = avatar_url
    db.add(current_user)
    await db.commit()
    await db.refresh(current_user)

    return APIResponse(
        success=True,
        message="Avatar uploaded successfully",
        data={"avatar_url": avatar_url}
    )
