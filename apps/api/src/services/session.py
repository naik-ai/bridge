"""
Session Service - manages user sessions and tokens.
Handles session creation, validation, refresh, and cleanup.

PDR Reference: §6 (Security & Access), §11 (Acceptance Criteria)
"""

import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.exceptions import InvalidTokenException, SessionExpiredException
from src.models.db_models import Session, User

logger = structlog.get_logger(__name__)


class SessionService:
    """
    Service for managing user sessions.

    Session Management (PDR §6):
    - Generate secure random tokens
    - Store in database with expiration
    - Validate tokens on each request
    - Auto-refresh expiring sessions
    - Clean up expired sessions

    PDR Acceptance: Sessions persisted in Postgres with expiration handling
    """

    def __init__(self, db: AsyncSession):
        """
        Initialize session service.

        Args:
            db: Database session
        """
        self.db = db

    async def create_session(
        self,
        user: User,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None,
    ) -> Session:
        """
        Create new session for user.

        Args:
            user: User model
            user_agent: User agent string from request
            ip_address: IP address from request

        Returns:
            Session model with token
        """
        # Generate secure random token
        token = self._generate_token()

        # Calculate expiration
        expires_at = datetime.now(timezone.utc) + timedelta(
            days=settings.session_expires_days
        )

        # Create session
        session = Session(
            user_id=user.id,
            token=token,
            expires_at=expires_at,
            created_at=datetime.now(timezone.utc),
            last_accessed=datetime.now(timezone.utc),
            user_agent=user_agent,
            ip_address=ip_address,
        )

        self.db.add(session)
        await self.db.flush()

        logger.info(
            "✨ session_created",
            user_id=str(user.id),
            session_id=str(session.id),
            expires_at=expires_at.isoformat(),
        )

        return session

    async def get_session_by_token(self, token: str) -> Optional[Session]:
        """
        Get session by token (without validation).

        Args:
            token: Session token

        Returns:
            Session or None
        """
        stmt = select(Session).where(Session.token == token)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def validate_session(self, token: str) -> tuple[Session, User]:
        """
        Validate session token and return session + user.

        Also handles auto-refresh of expiring sessions.

        Args:
            token: Session token

        Returns:
            Tuple of (Session, User)

        Raises:
            InvalidTokenException: If token not found
            SessionExpiredException: If session expired
        """
        # Get session
        session = await self.get_session_by_token(token)

        if not session:
            logger.warning("⚠️ session_not_found", token_preview=token[:20])
            raise InvalidTokenException()

        # Check expiration
        now = datetime.now(timezone.utc)
        if session.expires_at <= now:
            logger.warning(
                "⚠️ session_expired",
                session_id=str(session.id),
                expired_at=session.expires_at.isoformat(),
            )
            raise SessionExpiredException(expires_at=session.expires_at.isoformat())

        # Load user
        stmt = select(User).where(User.id == session.user_id)
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user or not user.is_active:
            logger.warning("⚠️ user_not_found_or_inactive", user_id=str(session.user_id))
            raise InvalidTokenException("User not found or inactive")

        # Update last accessed
        session.last_accessed = now
        await self.db.flush()

        # Auto-refresh if close to expiry
        await self._auto_refresh_if_needed(session)

        logger.debug(
            "✅ session_validated",
            session_id=str(session.id),
            user_id=str(user.id),
        )

        return session, user

    async def refresh_session(self, token: str) -> Session:
        """
        Refresh session expiration.

        Args:
            token: Session token

        Returns:
            Updated Session

        Raises:
            InvalidTokenException: If token not found
        """
        session = await self.get_session_by_token(token)

        if not session:
            raise InvalidTokenException()

        # Extend expiration
        session.expires_at = datetime.now(timezone.utc) + timedelta(
            days=settings.session_expires_days
        )
        await self.db.flush()

        logger.info(
            "🔄 session_refreshed",
            session_id=str(session.id),
            new_expires_at=session.expires_at.isoformat(),
        )

        return session

    async def invalidate_session(self, token: str) -> bool:
        """
        Invalidate (delete) session - used for logout.

        Args:
            token: Session token

        Returns:
            True if session was deleted, False if not found
        """
        session = await self.get_session_by_token(token)

        if not session:
            return False

        session_id = str(session.id)
        await self.db.delete(session)
        await self.db.flush()

        logger.info("🗑️ session_invalidated", session_id=session_id)
        return True

    async def invalidate_user_sessions(self, user_id: UUID) -> int:
        """
        Invalidate all sessions for a user.

        Useful for security actions like password reset or account suspension.

        Args:
            user_id: User ID

        Returns:
            Number of sessions invalidated
        """
        stmt = select(Session).where(Session.user_id == user_id)
        result = await self.db.execute(stmt)
        sessions = result.scalars().all()

        count = len(sessions)
        for session in sessions:
            await self.db.delete(session)

        await self.db.flush()

        logger.info(
            "🗑️ user_sessions_invalidated",
            user_id=str(user_id),
            count=count,
        )

        return count

    async def cleanup_expired_sessions(self) -> int:
        """
        Clean up expired sessions from database.

        Should be run periodically (e.g., daily cron job).

        Returns:
            Number of sessions deleted
        """
        now = datetime.now(timezone.utc)

        stmt = select(Session).where(Session.expires_at <= now)
        result = await self.db.execute(stmt)
        expired_sessions = result.scalars().all()

        count = len(expired_sessions)
        for session in expired_sessions:
            await self.db.delete(session)

        await self.db.flush()

        logger.info("🧹 expired_sessions_cleaned", count=count)
        return count

    async def get_user_sessions(self, user_id: UUID) -> list[Session]:
        """
        Get all active sessions for a user.

        Args:
            user_id: User ID

        Returns:
            List of Session models
        """
        now = datetime.now(timezone.utc)

        stmt = (
            select(Session)
            .where(Session.user_id == user_id)
            .where(Session.expires_at > now)
            .order_by(Session.last_accessed.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_session_info(self, token: str) -> dict:
        """
        Get session information (for debugging/monitoring).

        Args:
            token: Session token

        Returns:
            Dict with session info
        """
        session = await self.get_session_by_token(token)

        if not session:
            return {"exists": False}

        now = datetime.now(timezone.utc)
        time_until_expiry = (session.expires_at - now).total_seconds()

        return {
            "exists": True,
            "session_id": str(session.id),
            "user_id": str(session.user_id),
            "created_at": session.created_at.isoformat(),
            "expires_at": session.expires_at.isoformat(),
            "last_accessed": session.last_accessed.isoformat(),
            "expired": time_until_expiry <= 0,
            "time_until_expiry_seconds": max(0, int(time_until_expiry)),
            "user_agent": session.user_agent,
            "ip_address": session.ip_address,
        }

    async def _auto_refresh_if_needed(self, session: Session) -> None:
        """
        Auto-refresh session if close to expiry.

        Args:
            session: Session to potentially refresh
        """
        now = datetime.now(timezone.utc)
        time_until_expiry = (session.expires_at - now).total_seconds()
        threshold_seconds = settings.session_refresh_threshold_days * 86400

        if time_until_expiry < threshold_seconds:
            session.expires_at = now + timedelta(days=settings.session_expires_days)
            await self.db.flush()

            logger.info(
                "🔄 session_auto_refreshed",
                session_id=str(session.id),
                new_expires_at=session.expires_at.isoformat(),
            )

    @staticmethod
    def _generate_token() -> str:
        """
        Generate secure random session token.

        Returns:
            URL-safe token string
        """
        return secrets.token_urlsafe(32)
