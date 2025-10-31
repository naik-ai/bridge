"""
Precompute endpoint for Peter Dashboard Platform.
Handles manual cache warming for dashboards.

PDR Reference: §4 (Precompute Flow), §11 (Acceptance Criteria)
"""

import structlog
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from src.core.dependencies import get_current_user, get_precompute_service
from src.core.exceptions import DashboardNotFoundException
from src.core.response import ErrorCode, ResponseFactory
from src.models.db_models import User
from src.services.precompute import PrecomputeService

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/precompute", tags=["Precompute"])


# =============================================================================
# Request/Response Models
# =============================================================================


class PrecomputeRequest(BaseModel):
    """Request model for precompute."""

    slug: str = Field(..., description="Dashboard slug to precompute")


class PrecomputeResponse(BaseModel):
    """Response model for precompute."""

    slug: str
    success: bool
    cache_keys_populated: int
    queries_executed: int
    duration_ms: int
    as_of: str


# =============================================================================
# Endpoints
# =============================================================================


@router.post("")
async def precompute_dashboard(
    request: PrecomputeRequest,
    precompute_service: PrecomputeService = Depends(get_precompute_service),
    user: User = Depends(get_current_user),
) -> dict:
    """
    Manually warm cache for dashboard (precompute).

    PDR §4: "Precompute Flow - Operator or script invokes precompute endpoint with dashboard slug.
             API loads dashboard YAML, compiles queries, executes all queries on BigQuery in parallel.
             API transforms each result to chart payload format, stores in cache with fresh version identifier.
             API updates dashboard metadata with new as-of timestamp.
             Subsequent frontend requests hit warm cache until TTL expires or manual invalidation."

    PDR §11 Acceptance: "Precompute endpoint warms cache for specified dashboard"
                        "Manual precompute reduces subsequent load time to under 300ms"

    Use cases:
    - After ETL completion (scheduled precompute)
    - Before peak usage hours
    - After dashboard YAML updates
    - Manual refresh by operators

    Args:
        request: Precompute request with dashboard slug
        precompute_service: Precompute service
        user: Current authenticated user

    Returns:
        Precompute result with cache keys populated
    """
    try:
        logger.info(
            "precompute_requested",
            slug=request.slug,
            user_id=str(user.id),
        )

        result = await precompute_service.precompute_dashboard(
            slug=request.slug,
            user_id=str(user.id),
        )

        logger.info(
            "precompute_completed",
            slug=request.slug,
            cache_keys=result.get("cache_keys_populated", 0),
            queries=result.get("queries_executed", 0),
            duration_ms=result.get("duration_ms", 0),
        )

        return ResponseFactory.success(data=result)

    except DashboardNotFoundException as e:
        logger.warning("dashboard_not_found", slug=request.slug)
        return ResponseFactory.not_found_error(resource_type="dashboard", identifier=request.slug)

    except Exception as e:
        logger.error("precompute_failed", slug=request.slug, error=str(e))
        return ResponseFactory.error(
            error_code=ErrorCode.INTERNAL_SERVER_ERROR,
            message=f"Precompute failed: {str(e)}",
            status_code=500,
        )
