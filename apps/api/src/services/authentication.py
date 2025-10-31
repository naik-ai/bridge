"""
Authentication Service - Google OAuth integration with email allowlist.
Handles OAuth flow, token exchange, and email validation.

PDR Reference: §6 (Security & Access), §11 (Acceptance Criteria)
"""

import secrets
from datetime import datetime, timedelta
from typing import Any, Dict, Optional
from urllib.parse import urlencode

import httpx
import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.exceptions import AuthenticationException, AuthorizationException, EmailNotAllowedException
from src.models.db_models import User

logger = structlog.get_logger(__name__)


class AuthenticationService:
    """
    Service for Google OAuth authentication with email allowlist.

    OAuth Flow (PDR §6):
    1. User clicks login → redirect to Google OAuth
    2. User authorizes → Google redirects back with code
    3. Backend exchanges code for tokens
    4. Extract user email from ID token
    5. Check email against allowlist
    6. Create/update user record
    7. Create session and return token

    PDR §11 Acceptance: "Auth flow validates Google SSO token and checks allowlist"
    """

    # Google OAuth endpoints
    GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
    GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
    GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"

    def __init__(self, db: AsyncSession):
        """
        Initialize authentication service.

        Args:
            db: Database session
        """
        self.db = db

    def get_authorization_url(self, state: Optional[str] = None) -> str:
        """
        Generate Google OAuth authorization URL.

        Args:
            state: Optional state parameter for CSRF protection

        Returns:
            Authorization URL to redirect user to
        """
        if not state:
            state = secrets.token_urlsafe(32)

        params = {
            "client_id": settings.google_oauth_client_id,
            "redirect_uri": settings.google_oauth_redirect_uri,
            "response_type": "code",
            "scope": "openid email profile",
            "state": state,
            "access_type": "online",
            "prompt": "select_account",
        }

        url = f"{self.GOOGLE_AUTH_URL}?{urlencode(params)}"

        logger.info(
            "🔐 oauth_authorization_url_generated",
            state=state,
        )

        return url

    async def exchange_code_for_tokens(self, code: str) -> Dict[str, Any]:
        """
        Exchange authorization code for access token and ID token.

        Args:
            code: Authorization code from OAuth callback

        Returns:
            Dict with access_token, id_token, expires_in

        Raises:
            AuthenticationException: If token exchange fails
        """
        logger.info("🔄 exchanging_oauth_code", code_preview=code[:20])

        data = {
            "client_id": settings.google_oauth_client_id,
            "client_secret": settings.google_oauth_client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": settings.google_oauth_redirect_uri,
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.GOOGLE_TOKEN_URL,
                    data=data,
                    timeout=10.0,
                )

                if response.status_code != 200:
                    logger.error(
                        "❌ token_exchange_failed",
                        status=response.status_code,
                        error=response.text,
                    )
                    raise AuthenticationException(
                        f"Token exchange failed: {response.text}"
                    )

                tokens = response.json()

                logger.info("✅ oauth_tokens_received")
                return tokens

        except httpx.RequestError as e:
            logger.error("❌ token_exchange_request_failed", error=str(e))
            raise AuthenticationException(f"Failed to exchange code: {str(e)}")

    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """
        Get user information from Google using access token.

        Args:
            access_token: Google access token

        Returns:
            Dict with user info (email, name, etc.)

        Raises:
            AuthenticationException: If request fails
        """
        logger.info("🔍 fetching_user_info")

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self.GOOGLE_USERINFO_URL,
                    headers={"Authorization": f"Bearer {access_token}"},
                    timeout=10.0,
                )

                if response.status_code != 200:
                    logger.error(
                        "❌ user_info_fetch_failed",
                        status=response.status_code,
                        error=response.text,
                    )
                    raise AuthenticationException(
                        f"Failed to fetch user info: {response.text}"
                    )

                user_info = response.json()

                logger.info(
                    "✅ user_info_fetched",
                    email=user_info.get("email"),
                )

                return user_info

        except httpx.RequestError as e:
            logger.error("❌ user_info_request_failed", error=str(e))
            raise AuthenticationException(f"Failed to fetch user info: {str(e)}")

    def check_email_allowed(self, email: str) -> bool:
        """
        Check if email is in allowlist (PDR §6).

        Allowlist rules:
        1. Check exact email match in allowed_emails
        2. Check domain match in allowed_email_domains

        Args:
            email: User email address

        Returns:
            True if allowed, False otherwise
        """
        email_lower = email.lower()

        # Check exact email match
        if email_lower in settings.allowed_emails:
            logger.info("✅ email_allowed_exact_match", email=email)
            return True

        # Check domain match
        if "@" in email_lower:
            domain = email_lower.split("@")[1]
            if domain in settings.allowed_email_domains:
                logger.info("✅ email_allowed_domain_match", email=email, domain=domain)
                return True

        logger.warning("⚠️ email_not_allowed", email=email)
        return False

    async def authenticate_with_code(
        self, code: str
    ) -> tuple[User, Dict[str, Any]]:
        """
        Complete OAuth flow: exchange code, verify email, create/update user.

        Args:
            code: Authorization code from OAuth callback

        Returns:
            Tuple of (User, user_info_dict)

        Raises:
            AuthenticationException: If authentication fails
            EmailNotAllowedException: If email not in allowlist
        """
        logger.info("🔐 authenticating_with_oauth_code")

        # Exchange code for tokens
        tokens = await self.exchange_code_for_tokens(code)

        # Get user info
        user_info = await self.get_user_info(tokens["access_token"])

        email = user_info.get("email")
        if not email:
            raise AuthenticationException("No email in user info")

        # Check allowlist
        if not self.check_email_allowed(email):
            raise EmailNotAllowedException(email=email)

        # Create or update user
        user = await self._create_or_update_user(
            email=email,
            name=user_info.get("name"),
        )

        logger.info(
            "✅ user_authenticated",
            user_id=str(user.id),
            email=user.email,
        )

        return user, user_info

    async def _create_or_update_user(
        self, email: str, name: Optional[str] = None
    ) -> User:
        """
        Create new user or update existing user.

        Args:
            email: User email
            name: User name

        Returns:
            User model
        """
        # Check if user exists
        stmt = select(User).where(User.email == email.lower())
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()

        if user:
            # Update existing user
            user.last_login = datetime.utcnow()
            if name:
                user.name = name
            logger.info("♻️ user_updated", user_id=str(user.id), email=email)
        else:
            # Create new user
            user = User(
                email=email.lower(),
                name=name,
                created_at=datetime.utcnow(),
                last_login=datetime.utcnow(),
                is_active=True,
            )
            self.db.add(user)
            logger.info("✨ user_created", email=email)

        await self.db.flush()
        return user

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email.

        Args:
            email: User email

        Returns:
            User or None
        """
        stmt = select(User).where(User.email == email.lower())
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def deactivate_user(self, email: str) -> bool:
        """
        Deactivate user (soft delete).

        Args:
            email: User email

        Returns:
            True if user was deactivated, False if not found
        """
        user = await self.get_user_by_email(email)
        if not user:
            return False

        user.is_active = False
        await self.db.flush()

        logger.info("🚫 user_deactivated", user_id=str(user.id), email=email)
        return True

    async def reactivate_user(self, email: str) -> bool:
        """
        Reactivate user.

        Args:
            email: User email

        Returns:
            True if user was reactivated, False if not found
        """
        user = await self.get_user_by_email(email)
        if not user:
            return False

        user.is_active = True
        await self.db.flush()

        logger.info("✅ user_reactivated", user_id=str(user.id), email=email)
        return True
