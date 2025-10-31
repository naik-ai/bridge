"""
Health check endpoint for Peter Dashboard Platform.
Checks database, cache, and BigQuery connectivity.

PDR Reference: §3 (Architecture Overview), §11 (Acceptance Criteria)
"""

from datetime import datetime

import structlog
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.cache import CacheInterface
from src.core.dependencies import get_bigquery_dependency, get_cache_dependency, get_session_db
from src.core.response import ResponseFactory
from src.integrations.bigquery_client import BigQueryClient

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("")
async def health_check(
    db: AsyncSession = Depends(get_session_db),
    cache: CacheInterface = Depends(get_cache_dependency),
    bq_client: BigQueryClient = Depends(get_bigquery_dependency),
) -> dict:
    """
    Health check endpoint.

    Checks connectivity to:
    - Database (Postgres)
    - Cache (Redis or in-memory)
    - BigQuery

    PDR §11: "Dashboard validate endpoint rejects invalid YAML"
    Note: This is the health endpoint, not validation - accepts all requests.

    Returns:
        Health status with component statuses
    """
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "components": {},
    }

    # Check database
    try:
        result = await db.execute(text("SELECT 1"))
        result.scalar_one()
        health_status["components"]["database"] = {"status": "healthy", "type": "postgres"}
    except Exception as e:
        logger.error("health_database_check_failed", error=str(e))
        health_status["status"] = "degraded"
        health_status["components"]["database"] = {
            "status": "unhealthy",
            "error": str(e),
            "type": "postgres",
        }

    # Check cache
    try:
        test_key = "health_check_ping"
        test_value = f"pong_{datetime.utcnow().timestamp()}"
        await cache.set(test_key, test_value, ttl=10)
        retrieved = await cache.get(test_key)

        if retrieved == test_value:
            health_status["components"]["cache"] = {"status": "healthy", "type": cache.__class__.__name__}
        else:
            health_status["status"] = "degraded"
            health_status["components"]["cache"] = {
                "status": "unhealthy",
                "error": "Value mismatch",
                "type": cache.__class__.__name__,
            }
    except Exception as e:
        logger.error("health_cache_check_failed", error=str(e))
        health_status["status"] = "degraded"
        health_status["components"]["cache"] = {
            "status": "unhealthy",
            "error": str(e),
            "type": cache.__class__.__name__,
        }

    # Check BigQuery (dry run a simple query)
    try:
        # Simple query to check connectivity - dry run only, no execution
        test_query = "SELECT 1 as health_check"
        await bq_client.dry_run(test_query)
        health_status["components"]["bigquery"] = {"status": "healthy", "project": bq_client.project_id}
    except Exception as e:
        logger.error("health_bigquery_check_failed", error=str(e))
        health_status["status"] = "degraded"
        health_status["components"]["bigquery"] = {
            "status": "unhealthy",
            "error": str(e),
            "project": bq_client.project_id,
        }

    return ResponseFactory.success(data=health_status)
