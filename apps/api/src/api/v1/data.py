"""
Data serving endpoint for Peter Dashboard Platform.
Serves cached/fresh data for dashboards with cache-first strategy.

PDR Reference: §5 (Caching & Freshness Model), §9 (Performance & Cost Guardrails)
"""

from typing import Optional

import structlog
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

from src.core.dependencies import get_current_user, get_data_serving_service
from src.core.exceptions import DashboardNotFoundException
from src.core.response import ErrorCode, ResponseFactory
from src.models.db_models import User
from src.services.data_serving import DataServingService

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/data", tags=["Data"])


# =============================================================================
# Request/Response Models
# =============================================================================


class DataResponse(BaseModel):
    """Response model for data serving."""

    slug: str
    charts: dict  # Chart ID -> data payload
    as_of: str  # Timestamp when data was generated
    cache_hit: bool
    version: int


# =============================================================================
# Endpoints
# =============================================================================


@router.get("/{slug}")
async def get_dashboard_data(
    slug: str,
    force_refresh: bool = Query(False, description="Force cache refresh"),
    data_service: DataServingService = Depends(get_data_serving_service),
    user: User = Depends(get_current_user),
) -> dict:
    """
    Serve dashboard data with cache-first strategy.

    PDR §5: "Dashboard Data Serving Flow - Frontend requests dashboard via slug identifier.
             API checks session validity, retrieves dashboard metadata from Postgres.
             API determines if cache contains fresh results using key pattern.
             On cache hit: serialize and return immediately.
             On cache miss: load YAML, compile to execution plan, execute queries in parallel on BigQuery,
             transform results to compact chart payloads, store in cache with version marker, return to frontend."

    PDR §9: "Performance Targets - Dashboard load from warm cache: p95 under 300ms.
             Dashboard load from cold (cache miss): p95 under 1.5 seconds."

    PDR §11 Acceptance:
    - "Data serving endpoint returns cached results in under 300ms on repeat request"
    - "Data serving endpoint executes queries on cache miss and populates cache"

    Features:
    - Cache-first strategy (<300ms on hit)
    - Parallel query execution on cache miss
    - Compact payload transformation
    - Includes as-of timestamp for freshness
    - Version-aware caching

    Args:
        slug: Dashboard slug identifier
        force_refresh: Force cache refresh (skip cache)
        data_service: Data serving service
        user: Current authenticated user

    Returns:
        Dashboard data with chart payloads
    """
    try:
        logger.info(
            "data_request_received",
            slug=slug,
            user_id=str(user.id),
            force_refresh=force_refresh,
        )

        # Serve data (cache-first or fresh)
        result = await data_service.serve_dashboard_data(
            slug=slug,
            force_refresh=force_refresh,
        )

        logger.info(
            "data_served",
            slug=slug,
            cache_hit=result["cache_hit"],
            chart_count=len(result["charts"]),
            as_of=result["as_of"],
        )

        return ResponseFactory.success(data=result)

    except DashboardNotFoundException as e:
        logger.warning("dashboard_not_found", slug=slug)
        return ResponseFactory.not_found_error(resource_type="dashboard", identifier=slug)

    except Exception as e:
        logger.error("data_serving_failed", slug=slug, error=str(e))
        return ResponseFactory.error(
            error_code=ErrorCode.INTERNAL_SERVER_ERROR,
            message=f"Failed to serve data: {str(e)}",
            status_code=500,
        )
