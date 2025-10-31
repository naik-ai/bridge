"""
SQL Executor Service - executes queries with verification loop support.
Handles SQL execution, result transformation, and metadata extraction.

PDR Reference: §4 (Data & Control Flows - SQL Verification Loop), §9 (Performance & Cost Guardrails), §11 (Acceptance Criteria)
"""

import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.exceptions import BigQueryException, BytesLimitExceededException, QueryTimeoutException
from src.integrations.bigquery_client import BigQueryClient
from src.models.db_models import QueryLog, QueryPurpose
from src.models.yaml_schema import SQLVerificationResult

logger = structlog.get_logger(__name__)


class SQLExecutorService:
    """
    Service for executing SQL queries with guardrails.

    Features (PDR §4, §9):
    - Execute queries with maximum_bytes_billed cap
    - Return metadata + sample rows for verification
    - Transform results to compact payloads
    - Log query execution for cost tracking

    PDR §11 Acceptance:
    - "SQL run endpoint executes on BigQuery and returns metadata plus max 100 sample rows"
    - "SQL run enforces maximum_bytes_billed cap and fails queries exceeding limit"
    """

    def __init__(self, db: AsyncSession, bq_client: BigQueryClient):
        """
        Initialize SQL executor service.

        Args:
            db: Database session for query logging
            bq_client: BigQuery client
        """
        self.db = db
        self.bq_client = bq_client

    async def execute_for_verification(
        self,
        sql: str,
        max_bytes_billed: Optional[int] = None,
        user_id: Optional[str] = None,
        dashboard_id: Optional[str] = None,
    ) -> SQLVerificationResult:
        """
        Execute SQL for LLM verification loop (PDR §4).

        Returns metadata + max 100 sample rows for agent verification.
        Enforces bytes cap and logs execution.

        Args:
            sql: SQL query to execute
            max_bytes_billed: Optional bytes limit override
            user_id: User ID for logging
            dashboard_id: Dashboard ID for logging

        Returns:
            SQLVerificationResult with metadata and sample rows

        Raises:
            BigQueryException: If execution fails
            BytesLimitExceededException: If query exceeds bytes limit
        """
        query_hash = self.bq_client.hash_query(sql)

        logger.info(
            "🔍 executing_verification_query",
            query_hash=query_hash,
            sql_preview=sql[:100],
            max_bytes=max_bytes_billed or settings.bigquery_max_bytes_billed,
        )

        try:
            # Execute with guardrails
            result = await self.bq_client.execute_for_verification(
                sql=sql,
                max_bytes_billed=max_bytes_billed,
            )

            # Log successful execution
            await self._log_query_execution(
                sql=sql,
                query_hash=query_hash,
                bytes_scanned=result["bytes_scanned"],
                duration_ms=result["duration_ms"],
                row_count=result["row_count"],
                job_id=result["job_id"],
                cache_hit=result["cache_hit"],
                purpose=QueryPurpose.verification,
                user_id=user_id,
                dashboard_id=dashboard_id,
            )

            logger.info(
                "✅ verification_query_completed",
                query_hash=query_hash,
                rows=result["row_count"],
                bytes_scanned=result["bytes_scanned"],
                cache_hit=result["cache_hit"],
                duration_ms=result["duration_ms"],
            )

            return SQLVerificationResult(
                valid=True,
                job_id=result["job_id"],
                schema=result["schema"],
                row_count=result["row_count"],
                sample_rows=result["sample_rows"],
                bytes_scanned=result["bytes_scanned"],
                bytes_billed=result["bytes_billed"],
                cache_hit=result["cache_hit"],
                duration_ms=result["duration_ms"],
            )

        except Exception as e:
            logger.error(
                "❌ verification_query_failed",
                query_hash=query_hash,
                error=str(e),
            )

            # Log failed execution
            await self._log_query_execution(
                sql=sql,
                query_hash=query_hash,
                bytes_scanned=0,
                duration_ms=0,
                row_count=0,
                job_id=None,
                cache_hit=False,
                purpose=QueryPurpose.verification,
                user_id=user_id,
                dashboard_id=dashboard_id,
            )

            # Return error result
            return SQLVerificationResult(
                valid=False,
                error=str(e),
            )

    async def execute_for_serving(
        self,
        sql: str,
        max_bytes_billed: Optional[int] = None,
        user_id: Optional[str] = None,
        dashboard_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Execute SQL for data serving (returns all results).

        Used for dashboard data serving and precompute.
        Returns full result set (not limited to 100 rows).

        Args:
            sql: SQL query to execute
            max_bytes_billed: Optional bytes limit override
            user_id: User ID for logging
            dashboard_id: Dashboard ID for logging

        Returns:
            List of all result rows

        Raises:
            BigQueryException: If execution fails
        """
        query_hash = self.bq_client.hash_query(sql)

        logger.info(
            "📊 executing_serving_query",
            query_hash=query_hash,
            sql_preview=sql[:100],
        )

        try:
            # Execute and get all results
            rows = await self.bq_client.execute_for_serving(sql=sql)

            # Get metadata from last job (for logging)
            # Note: In production, we'd track the job more explicitly
            # For MVP, we'll use approximate values

            logger.info(
                "✅ serving_query_completed",
                query_hash=query_hash,
                rows=len(rows),
            )

            # Log execution (approximate bytes since we don't have job metadata here)
            await self._log_query_execution(
                sql=sql,
                query_hash=query_hash,
                bytes_scanned=0,  # TODO: Get from job metadata
                duration_ms=0,  # TODO: Get from job metadata
                row_count=len(rows),
                job_id=None,
                cache_hit=False,
                purpose=QueryPurpose.serving,
                user_id=user_id,
                dashboard_id=dashboard_id,
            )

            return rows

        except Exception as e:
            logger.error(
                "❌ serving_query_failed",
                query_hash=query_hash,
                error=str(e),
            )
            raise BigQueryException(
                message=f"Query execution failed: {str(e)}",
                query_hash=query_hash,
                original_error=e,
            )

    async def execute_batch(
        self,
        queries: List[Dict[str, Any]],
        user_id: Optional[str] = None,
        dashboard_id: Optional[str] = None,
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Execute multiple queries in parallel (PDR §4 - parallel execution).

        Args:
            queries: List of query dicts with 'id' and 'sql' keys
            user_id: User ID for logging
            dashboard_id: Dashboard ID for logging

        Returns:
            Dict mapping query_id to result rows
        """
        logger.info(
            "🚀 executing_batch_queries",
            query_count=len(queries),
            dashboard_id=dashboard_id,
        )

        # Execute all queries in parallel
        tasks = [
            self._execute_single_for_batch(
                query_id=q["id"],
                sql=q["sql"],
                max_bytes_billed=q.get("max_bytes_billed"),
                user_id=user_id,
                dashboard_id=dashboard_id,
            )
            for q in queries
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Build result dict
        result_map = {}
        for i, query in enumerate(queries):
            query_id = query["id"]
            result = results[i]

            if isinstance(result, Exception):
                logger.error(
                    "❌ batch_query_failed",
                    query_id=query_id,
                    error=str(result),
                )
                # Store empty result for failed queries
                result_map[query_id] = []
            else:
                result_map[query_id] = result

        logger.info(
            "✅ batch_execution_completed",
            query_count=len(queries),
            successful=sum(1 for r in results if not isinstance(r, Exception)),
            failed=sum(1 for r in results if isinstance(r, Exception)),
        )

        return result_map

    async def _execute_single_for_batch(
        self,
        query_id: str,
        sql: str,
        max_bytes_billed: Optional[int] = None,
        user_id: Optional[str] = None,
        dashboard_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Execute single query for batch execution.

        Args:
            query_id: Query identifier
            sql: SQL query
            max_bytes_billed: Optional bytes limit
            user_id: User ID for logging
            dashboard_id: Dashboard ID for logging

        Returns:
            List of result rows
        """
        return await self.execute_for_serving(
            sql=sql,
            max_bytes_billed=max_bytes_billed,
            user_id=user_id,
            dashboard_id=dashboard_id,
        )

    async def _log_query_execution(
        self,
        sql: str,
        query_hash: str,
        bytes_scanned: int,
        duration_ms: int,
        row_count: int,
        job_id: Optional[str],
        cache_hit: bool,
        purpose: QueryPurpose,
        user_id: Optional[str] = None,
        dashboard_id: Optional[str] = None,
    ) -> None:
        """
        Log query execution to database for cost tracking (PDR §7).

        Args:
            sql: SQL query
            query_hash: Query hash
            bytes_scanned: Bytes scanned
            duration_ms: Duration in milliseconds
            row_count: Number of rows returned
            job_id: BigQuery job ID
            cache_hit: Whether query hit cache
            purpose: Query purpose (verification/serving/precompute)
            user_id: User ID
            dashboard_id: Dashboard ID
        """
        try:
            log_entry = QueryLog(
                dashboard_id=dashboard_id,
                user_id=user_id,
                query_hash=query_hash,
                sql_preview=sql[:500],  # Store first 500 chars
                bytes_scanned=bytes_scanned,
                duration_ms=duration_ms,
                row_count=row_count,
                job_id=job_id,
                cache_hit=cache_hit,
                purpose=purpose,
                executed_at=datetime.utcnow(),
            )

            self.db.add(log_entry)
            await self.db.flush()

            logger.debug(
                "📝 query_logged",
                query_hash=query_hash,
                bytes_scanned=bytes_scanned,
                cost_usd=log_entry.estimated_cost_usd,
            )

        except Exception as e:
            logger.error(
                "❌ query_log_failed",
                query_hash=query_hash,
                error=str(e),
            )
            # Don't raise - logging failure shouldn't break query execution

    def transform_to_compact_payload(
        self,
        rows: List[Dict[str, Any]],
        chart_type: str,
    ) -> Dict[str, Any]:
        """
        Transform query results to compact chart payload (PDR §9).

        Target: <100KB per chart payload.
        Uses arrays instead of verbose objects where possible.

        Args:
            rows: Query result rows
            chart_type: Chart type (line_chart, bar_chart, etc.)

        Returns:
            Compact payload dict
        """
        if not rows:
            return {"data": [], "row_count": 0}

        # For time series charts: use [timestamp, value] arrays
        if chart_type in ["line_chart", "area_chart"]:
            return self._transform_time_series(rows)

        # For bar charts: use compact key-value format
        elif chart_type == "bar_chart":
            return self._transform_categorical(rows)

        # For KPI: single value
        elif chart_type == "kpi":
            return self._transform_kpi(rows)

        # For tables: return as-is but limit columns
        elif chart_type == "table":
            return self._transform_table(rows)

        # Default: return rows with minimal processing
        else:
            return {"data": rows, "row_count": len(rows)}

    def _transform_time_series(self, rows: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Transform to time series format: [[timestamp, value], ...]"""
        # Assume first column is timestamp, second is value
        # This is a simplified implementation - production would use schema info
        data = []
        for row in rows:
            keys = list(row.keys())
            if len(keys) >= 2:
                data.append([row[keys[0]], row[keys[1]]])

        return {"data": data, "row_count": len(rows), "format": "time_series"}

    def _transform_categorical(self, rows: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Transform to categorical format: {category: value}"""
        data = {}
        for row in rows:
            keys = list(row.keys())
            if len(keys) >= 2:
                data[str(row[keys[0]])] = row[keys[1]]

        return {"data": data, "row_count": len(rows), "format": "categorical"}

    def _transform_kpi(self, rows: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Transform to KPI format: single value"""
        if not rows:
            return {"value": None, "format": "kpi"}

        first_row = rows[0]
        keys = list(first_row.keys())
        value = first_row[keys[0]] if keys else None

        return {"value": value, "row_count": len(rows), "format": "kpi"}

    def _transform_table(self, rows: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Transform to table format: keep as rows but add metadata"""
        return {
            "data": rows,
            "row_count": len(rows),
            "columns": list(rows[0].keys()) if rows else [],
            "format": "table",
        }
