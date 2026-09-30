from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime, timedelta

from app.schemas.common import APIResponse
from app.schemas.auth import (
    UserRegister, UserLogin, TokenResponse, OAuthLoginRequest,
    PasswordResetRequest, PasswordResetConfirm, EmailVerificationRequest
)
from app.core.dependencies import get_db, get_current_user
from app.models.user import User, UserSession
from app.models.settings import UserSettings
from app.models.auth_metadata import AuthMetadata
from app.auth.jwt import hash_password, verify_password, create_access_token, generate_secure_token
from app.auth.session_manager import session_manager
import uuid

router = APIRouter()

@router.post("/register", response_model=APIResponse[TokenResponse], status_code=status.HTTP_201_CREATED)
async def register_user(payload: UserRegister, response: Response, request: Request, db: AsyncSession = Depends(get_db)):
    """Register a new user account with email & password"""
    existing = await db.execute(select(User).filter(User.email == payload.email))
    if existing.scalars().first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email is already registered")

    user_id = str(uuid.uuid4())
    new_user = User(
        id=user_id,
        email=payload.email,
        password_hash=hash_password(payload.password),
        full_name=payload.full_name or "New User",
        provider_type="credentials",
        role="user",
        is_active=True,
        is_verified=False,
    )
    db.add(new_user)
    
    # Initialize default settings and auth metadata
    db.add(UserSettings(id=str(uuid.uuid4()), user_id=user_id))
    verification_token = generate_secure_token(32)
    db.add(AuthMetadata(
        id=str(uuid.uuid4()),
        user_id=user_id,
        last_login_at=datetime.utcnow(),
        login_count=1,
        email_verification_token=verification_token,
        email_verification_expires=datetime.utcnow() + timedelta(days=1)
    ))
    
    await db.commit()
    await db.refresh(new_user)

    # Create DB Session and JWT Token
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("User-Agent")
    session = await session_manager.create_session(db, user_id=new_user.id, ip_address=client_ip, user_agent=user_agent)

    token = create_access_token({"sub": new_user.id, "email": new_user.email, "role": new_user.role})

    # Set secure session cookie
    response.set_cookie(key="aethermind_token", value=token, httponly=True, samesite="lax", max_age=86400 * 7)

    return APIResponse(
        success=True,
        message="Account registered successfully. Verification token generated.",
        data=TokenResponse(
            access_token=token,
            user_id=new_user.id,
            email=new_user.email,
            full_name=new_user.full_name,
            avatar_url=new_user.avatar_url,
            role=new_user.role,
            is_verified=new_user.is_verified,
        )
    )

@router.post("/login", response_model=APIResponse[TokenResponse])
async def login_user(payload: UserLogin, response: Response, request: Request, db: AsyncSession = Depends(get_db)):
    """Authenticate user credentials and return JWT access token & create DB session"""
    result = await db.execute(select(User).filter(User.email == payload.email))
    user = result.scalars().first()
    if not user or not user.password_hash or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Account is disabled")

    # Update Auth Metadata
    meta_res = await db.execute(select(AuthMetadata).filter(AuthMetadata.user_id == user.id))
    meta = meta_res.scalars().first()
    if meta:
        meta.last_login_at = datetime.utcnow()
        meta.login_count += 1
    else:
        db.add(AuthMetadata(id=str(uuid.uuid4()), user_id=user.id, last_login_at=datetime.utcnow(), login_count=1))
    await db.commit()

    # Create DB Session and JWT Token
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("User-Agent")
    await session_manager.create_session(
        db, user_id=user.id, ip_address=client_ip, user_agent=user_agent, remember_me=payload.remember_me or False
    )

    token = create_access_token(
        {"sub": user.id, "email": user.email, "role": user.role}, remember_me=payload.remember_me or False
    )

    max_age = (86400 * 30) if payload.remember_me else (86400 * 7)
    response.set_cookie(key="aethermind_token", value=token, httponly=True, samesite="lax", max_age=max_age)

    return APIResponse(
        success=True,
        message="Login successful",
        data=TokenResponse(
            access_token=token,
            user_id=user.id,
            email=user.email,
            full_name=user.full_name,
            avatar_url=user.avatar_url,
            role=user.role,
            is_verified=user.is_verified,
        )
    )

@router.post("/oauth/google", response_model=APIResponse[TokenResponse])
async def google_oauth_login(payload: OAuthLoginRequest, response: Response, request: Request, db: AsyncSession = Depends(get_db)):
    """Authenticate or Register user via Google OAuth"""
    email = payload.email or f"google_{uuid.uuid4().hex[:8]}@aethermind.ai"
    result = await db.execute(select(User).filter(User.email == email))
    user = result.scalars().first()

    if not user:
        user = User(
            id=str(uuid.uuid4()),
            email=email,
            full_name=payload.full_name or "Google User",
            avatar_url=payload.avatar_url or "https://api.dicebear.com/7.x/avataaars/svg?seed=google",
            provider_type="google",
            role="user",
            is_active=True,
            is_verified=True,
        )
        db.add(user)
        db.add(UserSettings(id=str(uuid.uuid4()), user_id=user.id))
        db.add(AuthMetadata(id=str(uuid.uuid4()), user_id=user.id, last_login_at=datetime.utcnow(), login_count=1))
        await db.commit()
        await db.refresh(user)

    token = create_access_token({"sub": user.id, "email": user.email, "role": user.role})
    response.set_cookie(key="aethermind_token", value=token, httponly=True, samesite="lax", max_age=86400 * 7)

    return APIResponse(
        success=True,
        message="Google OAuth login successful",
        data=TokenResponse(
            access_token=token,
            user_id=user.id,
            email=user.email,
            full_name=user.full_name,
            avatar_url=user.avatar_url,
            role=user.role,
            is_verified=user.is_verified,
        )
    )

@router.post("/logout", response_model=APIResponse[dict])
async def logout_user(response: Response, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Revoke active user session and destroy authentication cookie"""
    await session_manager.invalidate_all_user_sessions(db, current_user.id)
    response.delete_cookie(key="aethermind_token")
    return APIResponse(success=True, message="Session destroyed and logged out successfully", data={"status": "logged_out"})

@router.post("/forgot-password", response_model=APIResponse[dict])
async def forgot_password(payload: PasswordResetRequest, db: AsyncSession = Depends(get_db)):
    """Trigger password reset token dispatch for user account"""
    result = await db.execute(select(User).filter(User.email == payload.email))
    user = result.scalars().first()
    if user:
        reset_token = generate_secure_token(32)
        meta_res = await db.execute(select(AuthMetadata).filter(AuthMetadata.user_id == user.id))
        meta = meta_res.scalars().first()
        if not meta:
            meta = AuthMetadata(id=str(uuid.uuid4()), user_id=user.id)
            db.add(meta)
        meta.password_reset_token = reset_token
        meta.password_reset_expires = datetime.utcnow() + timedelta(hours=1)
        await db.commit()
        return APIResponse(
            success=True,
            message="Password reset instructions dispatched to email",
            data={"email": payload.email, "reset_token": reset_token}
        )
    return APIResponse(
        success=True,
        message="If email exists, password reset instructions have been dispatched",
        data={"email": payload.email}
    )

@router.post("/reset-password", response_model=APIResponse[dict])
async def reset_password(payload: PasswordResetConfirm, db: AsyncSession = Depends(get_db)):
    """Reset user password using valid token"""
    meta_res = await db.execute(
        select(AuthMetadata).filter(
            AuthMetadata.password_reset_token == payload.token,
            AuthMetadata.password_reset_expires > datetime.utcnow()
        )
    )
    meta = meta_res.scalars().first()
    if not meta:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired reset token")

    user_res = await db.execute(select(User).filter(User.id == meta.user_id))
    user = user_res.scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user.password_hash = hash_password(payload.new_password)
    meta.password_reset_token = None
    meta.password_reset_expires = None
    db.add(user)
    db.add(meta)
    await db.commit()

    return APIResponse(success=True, message="Password reset successfully. You can now login.", data={"status": "password_reset"})

@router.post("/verify-email", response_model=APIResponse[dict])
async def verify_email(payload: EmailVerificationRequest, db: AsyncSession = Depends(get_db)):
    """Verify user email address using token"""
    meta_res = await db.execute(
        select(AuthMetadata).filter(AuthMetadata.email_verification_token == payload.token)
    )
    meta = meta_res.scalars().first()
    if not meta:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid verification token")

    user_res = await db.execute(select(User).filter(User.id == meta.user_id))
    user = user_res.scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user.is_verified = True
    meta.email_verification_token = None
    meta.email_verification_expires = None
    db.add(user)
    db.add(meta)
    await db.commit()

    return APIResponse(success=True, message="Email address verified successfully", data={"email": user.email, "is_verified": True})

@router.get("/verify-session", response_model=APIResponse[dict])
async def verify_session(current_user: User = Depends(get_current_user)):
    """Check if current user session is active and valid"""
    return APIResponse(
        success=True,
        message="Session active",
        data={
            "user_id": current_user.id,
            "email": current_user.email,
            "full_name": current_user.full_name,
            "role": current_user.role,
            "is_verified": current_user.is_verified
        }
    )
