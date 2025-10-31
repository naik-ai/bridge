"""
SQL verification endpoint for Peter Dashboard Platform.
Executes SQL queries with guardrails for LLM verification loop.

PDR Reference: §4 (Data & Control Flows - SQL Verification Loop), §9 (Performance & Cost Guardrails)
"""

from typing import Optional

import structlog
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from src.core.dependencies import get_current_user, get_sql_executor_service
from src.core.exceptions import BigQueryException, BytesLimitExceededException
from src.core.response import ErrorCode, ResponseFactory
from src.models.db_models import User
from src.models.yaml_schema import SQLVerificationResult
from src.services.sql_executor import SQLExecutorService

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/sql", tags=["SQL"])


# =============================================================================
# Request/Response Models
# =============================================================================


class SQLRunRequest(BaseModel):
    """Request model for SQL execution."""

    sql: str = Field(..., description="SQL query to execute", min_length=10)
    max_bytes_billed: Optional[int] = Field(
        default=None,
        description="Override max bytes billed (defaults to 100MB)",
        gt=0,
    )
    dashboard_slug: Optional[str] = Field(
        default=None,
        description="Dashboard slug for logging context",
    )


# =============================================================================
# Endpoints
# =============================================================================


@router.post("/run")
async def run_sql(
    request: SQLRunRequest,
    executor_service: SQLExecutorService = Depends(get_sql_executor_service),
    user: User = Depends(get_current_user),
) -> dict:
    """
    Execute SQL query with guardrails for verification.

    PDR §4: "SQL Verification Loop - Agent sends SQL to backend verification endpoint.
             Backend executes on BigQuery, returns metadata: column types, row counts,
             min/max values, sample data. Agent receives verification payload, not raw data."

    PDR §9: "Query Caps - Every query includes maximum_bytes_billed parameter set to 100 MB for MVP.
             Queries exceeding limit fail immediately."

    PDR §11 Acceptance:
    - "SQL run endpoint executes on BigQuery and returns metadata plus max 100 sample rows"
    - "SQL run enforces maximum_bytes_billed cap and fails queries exceeding limit"

    Features:
    - Enforces max_bytes_billed (100MB default, configurable)
    - Returns metadata + sample rows (max 100)
    - Uses BigQuery Result Cache
    - Logs execution for cost tracking

    Args:
        request: SQL run request with query and optional bytes limit
        executor_service: SQL executor service
        user: Current authenticated user

    Returns:
        SQL verification result with metadata and sample rows
    """
    try:
        logger.info(
            "sql_run_requested",
            user_id=str(user.id),
            sql_preview=request.sql[:100],
            max_bytes=request.max_bytes_billed,
            dashboard=request.dashboard_slug,
        )

        # Execute query with verification
        result = await executor_service.execute_for_verification(
            sql=request.sql,
            max_bytes_billed=request.max_bytes_billed,
            user_id=str(user.id),
            dashboard_id=request.dashboard_slug,
        )

        if result.valid:
            logger.info(
                "sql_run_successful",
                job_id=result.job_id,
                rows=result.row_count,
                bytes_scanned=result.bytes_scanned,
                cache_hit=result.cache_hit,
                duration_ms=result.duration_ms,
            )
        else:
            logger.warning("sql_run_invalid", error=result.error)

        return ResponseFactory.success(data=result.model_dump())

    except BytesLimitExceededException as e:
        logger.warning(
            "bytes_limit_exceeded",
            bytes_attempted=e.details.get("bytes_scanned"),
            max_allowed=e.details.get("max_bytes_allowed"),
        )
        return ResponseFactory.error(
            error_code=ErrorCode.BYTES_LIMIT_EXCEEDED,
            message=str(e),
            details=e.details,
            status_code=422,
        )

    except BigQueryException as e:
        logger.error("bigquery_execution_failed", error=str(e))
        return ResponseFactory.bigquery_error(
            message=str(e),
            bytes_scanned=e.details.get("bytes_scanned"),
            query_hash=e.details.get("query_hash"),
        )

    except Exception as e:
        logger.error("sql_run_failed", error=str(e))
        return ResponseFactory.error(
            error_code=ErrorCode.INTERNAL_SERVER_ERROR,
            message=f"SQL execution failed: {str(e)}",
            status_code=500,
        )
