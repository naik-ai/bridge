"""
Authentication endpoints for Peter Dashboard Platform.
Handles Google OAuth login flow, session management, and user info.

PDR Reference: §6 (Security & Access), §11 (Acceptance Criteria)
"""

from typing import Optional

import structlog
from fastapi import APIRouter, Depends, Header, Query
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

from src.core.dependencies import get_authentication_service, get_current_user, get_session_service
from src.core.exceptions import AuthenticationException, EmailNotAllowedException
from src.core.response import ErrorCode, ResponseFactory
from src.models.db_models import User
from src.services.authentication import AuthenticationService
from src.services.session import SessionService

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])


# =============================================================================
# Request/Response Models
# =============================================================================


class CallbackRequest(BaseModel):
    """Request model for OAuth callback."""

    code: str
    state: Optional[str] = None


class LoginResponse(BaseModel):
    """Response model for successful login."""

    token: str
    user: dict
    expires_at: str


class UserInfoResponse(BaseModel):
    """Response model for current user info."""

    id: str
    email: str
    name: str
    is_active: bool
    created_at: str


# =============================================================================
# Endpoints
# =============================================================================


@router.get("/login")
async def login(
    redirect_to: Optional[str] = Query(None, description="URL to redirect after login"),
    auth_service: AuthenticationService = Depends(get_authentication_service),
) -> RedirectResponse:
    """
    Initiate Google OAuth login flow.

    PDR §6: "Google OAuth 2.0 flow for user login. Redirect to Google, verify token, extract email."
    PDR §11: "Auth flow validates Google SSO token and checks allowlist"

    Args:
        redirect_to: Optional URL to redirect after successful login
        auth_service: Authentication service

    Returns:
        Redirect to Google OAuth authorization page
    """
    # Generate state token for CSRF protection
    # In production, store state in Redis with redirect_to
    state = redirect_to or "default"

    authorization_url = auth_service.get_authorization_url(state=state)

    logger.info("oauth_login_initiated", state=state, redirect_to=redirect_to)

    return RedirectResponse(url=authorization_url, status_code=302)


@router.get("/callback")
async def oauth_callback(
    code: str = Query(..., description="Authorization code from Google"),
    state: Optional[str] = Query(None, description="State parameter"),
    auth_service: AuthenticationService = Depends(get_authentication_service),
    session_service: SessionService = Depends(get_session_service),
) -> dict:
    """
    Handle OAuth callback from Google.

    PDR §6: "Handle OAuth callback, create session. Exchange code, check allowlist, create user, issue token."
    PDR §11: "Auth flow validates Google SSO token and checks allowlist"

    Flow:
    1. Exchange code for tokens
    2. Get user info from Google
    3. Check email allowlist
    4. Create/update user record
    5. Create session
    6. Return token

    Args:
        code: Authorization code from Google
        state: State parameter (for CSRF protection)
        auth_service: Authentication service
        session_service: Session service

    Returns:
        Login response with token and user info

    Raises:
        AuthenticationException: If token exchange fails
        EmailNotAllowedException: If email not in allowlist
    """
    try:
        logger.info("oauth_callback_received", state=state, code_preview=code[:20])

        # Authenticate with code (handles token exchange, user info, allowlist check, user creation)
        user, user_info = await auth_service.authenticate_with_code(code)

        # Create session
        session = await session_service.create_session(user=user)

        logger.info(
            "oauth_authentication_successful",
            user_id=str(user.id),
            email=user.email,
            session_id=str(session.id),
        )

        return ResponseFactory.success(
            data={
                "token": session.token,
                "user": {
                    "id": str(user.id),
                    "email": user.email,
                    "name": user.name,
                    "avatar_url": user.avatar_url,
                },
                "expires_at": session.expires_at.isoformat(),
            }
        )

    except EmailNotAllowedException as e:
        logger.warning("email_not_allowed", email=e.details.get("email"))
        return ResponseFactory.error(
            error_code=ErrorCode.EMAIL_NOT_ALLOWED,
            message=str(e),
            details=e.details,
            status_code=403,
        )

    except AuthenticationException as e:
        logger.error("authentication_failed", error=str(e))
        return ResponseFactory.error(
            error_code=ErrorCode.AUTHENTICATION_REQUIRED,
            message=str(e),
            status_code=401,
        )

    except Exception as e:
        logger.error("oauth_callback_failed", error=str(e))
        return ResponseFactory.error(
            error_code=ErrorCode.INTERNAL_SERVER_ERROR,
            message="Authentication failed",
            details={"error": str(e)},
            status_code=500,
        )


@router.post("/logout")
async def logout(
    authorization: Optional[str] = Header(None),
    session_service: SessionService = Depends(get_session_service),
) -> dict:
    """
    Logout user and invalidate session.

    PDR §6: "Invalidate session record in Postgres with expiration timestamp."

    Args:
        authorization: Authorization header with Bearer token
        session_service: Session service

    Returns:
        Success response
    """
    if not authorization or not authorization.startswith("Bearer "):
        logger.warning("logout_no_token")
        return ResponseFactory.success(data={"message": "Already logged out"})

    token = authorization.replace("Bearer ", "")

    try:
        await session_service.invalidate_session(token)

        logger.info("session_invalidated")

        return ResponseFactory.success(data={"message": "Logged out successfully"})

    except Exception as e:
        logger.error("logout_failed", error=str(e))
        # Still return success - logout should be idempotent
        return ResponseFactory.success(data={"message": "Logged out"})


@router.get("/me")
async def get_current_user_info(
    user: User = Depends(get_current_user),
) -> dict:
    """
    Get current authenticated user information.

    PDR §6: "Return current user info from session token."

    Args:
        user: Current authenticated user

    Returns:
        User information
    """
    logger.info("get_user_info", user_id=str(user.id), email=user.email)

    return ResponseFactory.success(
        data={
            "id": str(user.id),
            "email": user.email,
            "name": user.name,
            "avatar_url": user.avatar_url,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat(),
        }
    )
