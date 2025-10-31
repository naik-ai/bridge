"""
FastAPI dependency injection factories for services.
Follows fee-admin-standalone patterns with constructor injection.

PDR Reference: §3 (Architecture Overview), §11 (Acceptance Criteria)
"""

from typing import Annotated, Optional

from fastapi import Depends, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.cache import CacheInterface, get_cache
from src.core.exceptions import AuthenticationException, SessionExpiredException
from src.db.database import get_db
from src.integrations.bigquery_client import BigQueryClient, get_bigquery_client
from src.models.db_models import Session as SessionModel
from src.models.db_models import User

# Import services (Phase 2 - Complete)
from src.services.authentication import AuthenticationService
from src.services.dashboard_compiler import DashboardCompilerService
from src.services.data_serving import DataServingService
from src.services.lineage import LineageService
from src.services.precompute import PrecomputeService
from src.services.schema import SchemaService
from src.services.session import SessionService
from src.services.sql_executor import SQLExecutorService
from src.services.storage import StorageService
from src.services.yaml_validation import YAMLValidationService


# =============================================================================
# Core Dependencies
# =============================================================================


async def get_session_db() -> AsyncSession:
    """Get database session dependency."""
    async for session in get_db():
        yield session


def get_cache_dependency() -> CacheInterface:
    """Get cache instance dependency."""
    return get_cache()


def get_bigquery_dependency() -> BigQueryClient:
    """Get BigQuery client dependency."""
    return get_bigquery_client()


# =============================================================================
# Authentication Dependencies
# =============================================================================


async def get_current_user_optional(
    authorization: Annotated[Optional[str], Header()] = None,
    db: AsyncSession = Depends(get_session_db),
) -> Optional[User]:
    """
    Get current user from session token (optional).
    Returns None if no token provided or invalid token.

    Args:
        authorization: Authorization header (Bearer token)
        db: Database session

    Returns:
        User or None
    """
    if not authorization:
        return None

    if not authorization.startswith("Bearer "):
        return None

    token = authorization.replace("Bearer ", "")

    # Import here to avoid circular dependency
    from datetime import datetime, timezone

    from sqlalchemy import select

    # Look up session
    stmt = (
        select(SessionModel)
        .where(SessionModel.token == token)
        .where(SessionModel.expires_at > datetime.now(timezone.utc))
    )
    result = await db.execute(stmt)
    session = result.scalar_one_or_none()

    if not session:
        return None

    # Load user
    stmt = select(User).where(User.id == session.user_id).where(User.is_active == True)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    return user


async def get_current_user(
    user: Optional[User] = Depends(get_current_user_optional),
) -> User:
    """
    Get current user from session token (required).
    Raises exception if not authenticated.

    Args:
        user: Optional user from get_current_user_optional

    Returns:
        User

    Raises:
        HTTPException: If not authenticated
    """
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")

    return user


async def require_auth(
    authorization: Annotated[Optional[str], Header()] = None,
    db: AsyncSession = Depends(get_session_db),
) -> tuple[User, SessionModel]:
    """
    Require authentication and return user + session.
    Validates token and session expiry.

    Args:
        authorization: Authorization header (Bearer token)
        db: Database session

    Returns:
        Tuple of (User, Session)

    Raises:
        AuthenticationException: If not authenticated
        SessionExpiredException: If session expired
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise AuthenticationException("No authorization token provided")

    token = authorization.replace("Bearer ", "")

    # Import here to avoid circular dependency
    from datetime import datetime, timezone

    from sqlalchemy import select

    # Look up session
    stmt = select(SessionModel).where(SessionModel.token == token)
    result = await db.execute(stmt)
    session = result.scalar_one_or_none()

    if not session:
        raise AuthenticationException("Invalid session token")

    # Check expiry
    if session.expires_at <= datetime.now(timezone.utc):
        raise SessionExpiredException(expires_at=session.expires_at.isoformat())

    # Load user
    stmt = select(User).where(User.id == session.user_id).where(User.is_active == True)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise AuthenticationException("User not found or inactive")

    return user, session


# =============================================================================
# Service Factory Dependencies (Phase 2 - Complete)
# =============================================================================


def get_yaml_validation_service(
    db: AsyncSession = Depends(get_session_db),
    bq_client: BigQueryClient = Depends(get_bigquery_dependency),
) -> YAMLValidationService:
    """Get YAML validation service instance."""
    return YAMLValidationService(db=db, bq_client=bq_client)


def get_dashboard_compiler_service(
    db: AsyncSession = Depends(get_session_db),
) -> DashboardCompilerService:
    """Get dashboard compiler service instance."""
    return DashboardCompilerService(db=db)


def get_sql_executor_service(
    db: AsyncSession = Depends(get_session_db),
    bq_client: BigQueryClient = Depends(get_bigquery_dependency),
) -> SQLExecutorService:
    """Get SQL executor service instance."""
    return SQLExecutorService(db=db, bq_client=bq_client)


def get_data_serving_service(
    db: AsyncSession = Depends(get_session_db),
    cache: CacheInterface = Depends(get_cache_dependency),
    bq_client: BigQueryClient = Depends(get_bigquery_dependency),
) -> DataServingService:
    """Get data serving service instance."""
    return DataServingService(db=db, cache=cache, bq_client=bq_client)


def get_precompute_service(
    db: AsyncSession = Depends(get_session_db),
    cache: CacheInterface = Depends(get_cache_dependency),
    bq_client: BigQueryClient = Depends(get_bigquery_dependency),
) -> PrecomputeService:
    """Get precompute service instance."""
    return PrecomputeService(db=db, cache=cache, bq_client=bq_client)


def get_storage_service() -> StorageService:
    """Get storage service instance (Phase 6: No DB dependency)."""
    return StorageService()


def get_lineage_service(
    db: AsyncSession = Depends(get_session_db),
    cache: CacheInterface = Depends(get_cache_dependency),
) -> LineageService:
    """Get lineage service instance."""
    return LineageService(db=db, cache=cache)


def get_authentication_service(
    db: AsyncSession = Depends(get_session_db),
) -> AuthenticationService:
    """Get authentication service instance."""
    return AuthenticationService(db=db)


def get_session_service(
    db: AsyncSession = Depends(get_session_db),
) -> SessionService:
    """Get session service instance."""
    return SessionService(db=db)


def get_schema_service(
    cache: CacheInterface = Depends(get_cache_dependency),
    bq_client: BigQueryClient = Depends(get_bigquery_dependency),
) -> SchemaService:
    """
    Get schema service instance.

    Args:
        cache: Cache interface for storing metadata
        bq_client: BigQuery client for schema operations

    Returns:
        SchemaService instance
    """
    return SchemaService(bq_client=bq_client, cache=cache)


# =============================================================================
# Testing Dependencies
# =============================================================================


def override_get_current_user(user: User):
    """Override for testing - inject a specific user."""

    async def _override():
        return user

    return _override


def override_skip_auth():
    """Override for testing - skip authentication entirely."""

    async def _override():
        # Return a mock user for testing
        return User(
            email="test@example.com",
            name="Test User",
            is_active=True,
        )

    return _override
