from typing import AsyncGenerator, Optional, List, Callable
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database.session import get_async_db
from app.auth.jwt import decode_access_token
from app.auth.session_manager import session_manager
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async for session in get_async_db():
        yield session

async def extract_token_from_request(request: Request, bearer_token: Optional[str] = None) -> Optional[str]:
    """Extracts authentication token from Authorization Header or HTTP Cookie"""
    if bearer_token:
        return bearer_token
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header.split(" ")[1]
    cookie_token = request.cookies.get("aethermind_token") or request.cookies.get("aethermind_session")
    if cookie_token:
        return cookie_token
    return None

async def get_current_user(
    request: Request,
    bearer_token: Optional[str] = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Dependency validating user identity from JWT Token or Session Cookie"""
    token = await extract_token_from_request(request, bearer_token)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token missing or invalid",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 1. Try standard JWT decoding
    payload = decode_access_token(token)
    user = None
    if payload and "sub" in payload:
        user_id = payload["sub"]
        result = await db.execute(select(User).filter(User.id == user_id))
        user = result.scalars().first()

    # 2. Try DB Session token lookup
    if not user:
        session = await session_manager.get_active_session(db, token)
        if session:
            result = await db.execute(select(User).filter(User.id == session.user_id))
            user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is disabled",
        )

    return user

async def get_optional_user(
    request: Request,
    bearer_token: Optional[str] = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """Retrieves user if token present, or None if anonymous"""
    try:
        return await get_current_user(request, bearer_token, db)
    except HTTPException:
        return None

async def get_current_user_or_session(
    request: Request,
    bearer_token: Optional[str] = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Returns the authenticated JWT user.
    If no token is provided, returns a session-isolated user scoped to the client.
    """
    user = await get_optional_user(request, bearer_token, db)
    if user:
        return user
    
    # Session-isolated fallback user (scoped per browser session cookie or header)
    session_id = request.headers.get("X-Session-ID") or request.cookies.get("aethermind_session")
    if not session_id:
        import uuid
        session_id = f"sess_guest_{uuid.uuid4().hex[:12]}"
    
    email = f"{session_id}@session.aethermind.ai"
    result = await db.execute(select(User).filter(User.email == email))
    user = result.scalars().first()
    if not user:
        user = User(
            id=session_id,
            email=email,
            full_name="Guest User",
            provider_type="session",
            role="user",
            is_active=True,
            is_verified=True,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
    return user

def require_role(allowed_roles: List[str]) -> Callable:
    """Role-based Access Control (RBAC) Dependency Builder"""
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.is_admin or current_user.role in allowed_roles:
            return current_user
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied. Requires one of roles: {', '.join(allowed_roles)}"
        )
    return role_checker
