from datetime import datetime, timedelta, timezone
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import uuid

from app.models.user import UserSession
from app.auth.jwt import generate_secure_token
from app.config.settings import settings

class SessionManager:
    """Enterprise Database Session Lifecycle Manager"""

    async def create_session(
        self,
        db: AsyncSession,
        user_id: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        remember_me: bool = False
    ) -> UserSession:
        """Creates and persists an active user session in database"""
        session_token = generate_secure_token(64)
        expire_days = settings.REMEMBER_ME_EXPIRE_DAYS if remember_me else 7
        expires_at = datetime.utcnow() + timedelta(days=expire_days)

        new_session = UserSession(
            id=str(uuid.uuid4()),
            user_id=user_id,
            session_token=session_token,
            ip_address=ip_address,
            user_agent=user_agent,
            remember_me=remember_me,
            is_active=True,
            expires_at=expires_at,
        )
        db.add(new_session)
        await db.commit()
        await db.refresh(new_session)
        return new_session

    async def get_active_session(self, db: AsyncSession, session_token: str) -> Optional[UserSession]:
        """Retrieves and validates an active user session"""
        result = await db.execute(
            select(UserSession).filter(
                UserSession.session_token == session_token,
                UserSession.is_active == True,
            )
        )
        session = result.scalars().first()
        if not session:
            return None

        if session.expires_at < datetime.utcnow():
            session.is_active = False
            db.add(session)
            await db.commit()
            return None

        return session

    async def invalidate_session(self, db: AsyncSession, session_token: str) -> bool:
        """Invalidates a single active session"""
        result = await db.execute(
            select(UserSession).filter(UserSession.session_token == session_token)
        )
        session = result.scalars().first()
        if session:
            session.is_active = False
            db.add(session)
            await db.commit()
            return True
        return False

    async def invalidate_all_user_sessions(self, db: AsyncSession, user_id: str) -> int:
        """Invalidates all sessions for a specific user"""
        result = await db.execute(
            select(UserSession).filter(
                UserSession.user_id == user_id,
                UserSession.is_active == True
            )
        )
        sessions = result.scalars().all()
        count = 0
        for s in sessions:
            s.is_active = False
            db.add(s)
            count += 1
        await db.commit()
        return count

session_manager = SessionManager()
