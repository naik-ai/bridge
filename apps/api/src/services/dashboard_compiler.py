"""
Dashboard Compiler Service - compiles YAML to execution plan.
Generates query execution plan and lineage graph seeds.

PDR Reference: §4 (Data & Control Flows), §7 (Lineage Tracking), §11 (Acceptance Criteria)
"""

import hashlib
from datetime import datetime
from typing import Any, Dict, List

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import CompilationException
from src.models.yaml_schema import CompilationResult, DashboardYAML

logger = structlog.get_logger(__name__)


class DashboardCompilerService:
    """
    Service for compiling dashboard YAML to execution plan.

    Compilation stages (PDR §4):
    1. Parse YAML (already validated)
    2. Generate query execution plan
    3. Build lineage graph seeds (dashboard → chart → query)
    4. Extract table references from SQL (basic for MVP)

    PDR §11 Acceptance: "Dashboard compile endpoint returns execution plan with query list and lineage seeds"
    """

    def __init__(self, db: AsyncSession):
        """
        Initialize dashboard compiler service.

        Args:
            db: Database session
        """
        self.db = db

    async def compile_dashboard(
        self,
        dashboard: DashboardYAML,
    ) -> CompilationResult:
        """
        Compile dashboard YAML to execution plan and lineage seeds.

        Args:
            dashboard: Validated dashboard YAML

        Returns:
            CompilationResult with execution plan and lineage

        Raises:
            CompilationException: If compilation fails
        """
        try:
            logger.info(
                "🔧 compiling_dashboard",
                slug=dashboard.metadata.slug,
                queries=len(dashboard.queries),
                charts=len(dashboard.layout),
            )

            # Stage 1: Generate execution plan
            execution_plan = self._build_execution_plan(dashboard)

            # Stage 2: Build lineage seeds
            lineage_nodes, lineage_edges = self._build_lineage_seeds(dashboard)

            result = CompilationResult(
                dashboard_slug=dashboard.metadata.slug,
                execution_plan=execution_plan,
                query_count=len(dashboard.queries),
                lineage_nodes=lineage_nodes,
                lineage_edges=lineage_edges,
                compiled_at=datetime.utcnow(),
            )

            logger.info(
                "✅ dashboard_compiled",
                slug=dashboard.metadata.slug,
                query_count=result.query_count,
                node_count=len(lineage_nodes),
                edge_count=len(lineage_edges),
            )

            return result

        except Exception as e:
            logger.error(
                "❌ compilation_failed",
                slug=dashboard.metadata.slug,
                error=str(e),
            )
            raise CompilationException(
                message=f"Failed to compile dashboard: {str(e)}",
                dashboard_slug=dashboard.metadata.slug,
                compilation_stage="execution_plan",
            )

    def _build_execution_plan(self, dashboard: DashboardYAML) -> Dict[str, Any]:
        """
        Build query execution plan.

        The execution plan defines:
        - Query order (MVP: parallel execution, no dependencies)
        - Query metadata (hash, SQL, parameters)
        - Chart-to-query mappings

        Args:
            dashboard: Validated dashboard YAML

        Returns:
            Execution plan dict
        """
        queries = []

        for query in dashboard.queries:
            # Generate query hash for cache keys (PDR §5)
            query_hash = self._hash_query(query.sql)

            # Find charts that use this query
            dependent_charts = [
                item.id for item in dashboard.layout if item.query_ref == query.id
            ]

            queries.append(
                {
                    "query_id": query.id,
                    "query_hash": query_hash,
                    "warehouse": query.warehouse.value,
                    "sql": query.sql,
                    "max_bytes_billed": query.max_bytes_billed,
                    "dependent_charts": dependent_charts,
                    "execution_order": 0,  # MVP: all parallel (order=0)
                }
            )

        # Build chart metadata
        charts = []
        for item in dashboard.layout:
            charts.append(
                {
                    "chart_id": item.id,
                    "chart_type": item.type.value,
                    "query_ref": item.query_ref,
                    "position": {
                        "x": item.position.x,
                        "y": item.position.y,
                        "w": item.position.w,
                        "h": item.position.h,
                    },
                    "config": item.chart.model_dump(),
                }
            )

        return {
            "dashboard_slug": dashboard.metadata.slug,
            "version": 1,  # TODO: Get from storage service
            "queries": queries,
            "charts": charts,
            "execution_strategy": "parallel",  # MVP: execute all queries in parallel
            "total_queries": len(queries),
            "total_charts": len(charts),
        }

    def _build_lineage_seeds(
        self, dashboard: DashboardYAML
    ) -> tuple[List[Dict[str, str]], List[Dict[str, str]]]:
        """
        Build lineage graph seeds (nodes and edges).

        Lineage structure (PDR §7):
        - Dashboard node
        - Chart nodes (one per layout item)
        - Query nodes (one per query)
        - Table nodes (extracted from SQL - basic for MVP)

        Edges:
        - Dashboard contains Chart
        - Chart executes Query
        - Query reads_from Table

        Args:
            dashboard: Validated dashboard YAML

        Returns:
            Tuple of (nodes, edges) as dicts
        """
        nodes: List[Dict[str, str]] = []
        edges: List[Dict[str, str]] = []

        slug = dashboard.metadata.slug

        # Dashboard node
        nodes.append(
            {
                "node_type": "dashboard",
                "node_id": slug,
                "metadata": {
                    "name": dashboard.metadata.name,
                    "owner": dashboard.metadata.owner,
                    "view_type": dashboard.metadata.view_type.value,
                },
            }
        )

        # Chart nodes + Dashboard→Chart edges
        for item in dashboard.layout:
            chart_id = f"{slug}:chart:{item.id}"

            nodes.append(
                {
                    "node_type": "chart",
                    "node_id": chart_id,
                    "metadata": {
                        "chart_type": item.type.value,
                        "title": item.chart.title,
                        "dashboard_slug": slug,
                    },
                }
            )

            # Dashboard contains Chart
            edges.append(
                {
                    "source_node_id": slug,
                    "source_node_type": "dashboard",
                    "target_node_id": chart_id,
                    "target_node_type": "chart",
                    "edge_type": "contains",
                }
            )

        # Query nodes + Chart→Query edges
        for query in dashboard.queries:
            query_id = f"{slug}:query:{query.id}"

            nodes.append(
                {
                    "node_type": "query",
                    "node_id": query_id,
                    "metadata": {
                        "warehouse": query.warehouse.value,
                        "query_hash": self._hash_query(query.sql),
                        "sql_preview": query.sql[:200],
                        "dashboard_slug": slug,
                    },
                }
            )

            # Chart executes Query (for each chart using this query)
            for item in dashboard.layout:
                if item.query_ref == query.id:
                    chart_id = f"{slug}:chart:{item.id}"
                    edges.append(
                        {
                            "source_node_id": chart_id,
                            "source_node_type": "chart",
                            "target_node_id": query_id,
                            "target_node_type": "query",
                            "edge_type": "executes",
                        }
                    )

            # Extract table references from SQL (basic parsing for MVP)
            table_refs = self._extract_table_references(query.sql)

            for table_ref in table_refs:
                # Table node
                nodes.append(
                    {
                        "node_type": "table",
                        "node_id": table_ref,
                        "metadata": {
                            "table_name": table_ref,
                        },
                    }
                )

                # Query reads_from Table
                edges.append(
                    {
                        "source_node_id": query_id,
                        "source_node_type": "query",
                        "target_node_id": table_ref,
                        "target_node_type": "table",
                        "edge_type": "reads_from",
                    }
                )

        return nodes, edges

    def _extract_table_references(self, sql: str) -> List[str]:
        """
        Extract table references from SQL.

        MVP implementation: regex-based extraction of `project.dataset.table` patterns.
        Future: Use sqlglot or sqlparse for proper SQL parsing (PDR §7).

        Args:
            sql: SQL query string

        Returns:
            List of fully-qualified table names
        """
        import re

        # Pattern for BigQuery fully-qualified table names
        # Matches: `project.dataset.table` or project.dataset.table
        pattern = r"`?([a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+)`?"

        matches = re.findall(pattern, sql)

        # Deduplicate and normalize
        tables = list(set(matches))

        logger.debug(
            "extracted_table_refs",
            count=len(tables),
            tables=tables[:5],  # Log first 5
        )

        return tables

    @staticmethod
    def _hash_query(sql: str) -> str:
        """
        Generate SHA256 hash of SQL query for cache keys.

        Args:
            sql: SQL query string

        Returns:
            Hex hash string
        """
        # Normalize: strip whitespace, convert to lowercase
        normalized = " ".join(sql.split()).lower()
        return hashlib.sha256(normalized.encode()).hexdigest()[:16]  # First 16 chars

    async def get_query_dependencies(self, dashboard: DashboardYAML) -> Dict[str, List[str]]:
        """
        Analyze query dependencies (for future optimization).

        MVP: All queries are independent (parallel execution).
        Future: Detect CTEs and dependent queries for sequential execution.

        Args:
            dashboard: Validated dashboard YAML

        Returns:
            Dict mapping query_id to list of dependent query_ids
        """
        # MVP: No dependencies
        return {query.id: [] for query in dashboard.queries}

    def estimate_execution_time(self, dashboard: DashboardYAML) -> Dict[str, Any]:
        """
        Estimate dashboard execution time (heuristic).

        Args:
            dashboard: Validated dashboard YAML

        Returns:
            Dict with estimated times
        """
        # Simple heuristic based on SQL complexity
        query_estimates = []

        for query in dashboard.queries:
            # Very rough estimates based on SQL characteristics
            sql_length = len(query.sql)
            has_join = "join" in query.sql.lower()
            has_aggregate = any(
                agg in query.sql.lower() for agg in ["sum(", "count(", "avg(", "group by"]
            )

            # Base estimate: 500ms
            estimate_ms = 500

            if sql_length > 1000:
                estimate_ms += 500
            if has_join:
                estimate_ms += 300
            if has_aggregate:
                estimate_ms += 200

            query_estimates.append(
                {
                    "query_id": query.id,
                    "estimated_ms": estimate_ms,
                }
            )

        # Overall dashboard estimate (parallel execution)
        max_query_time = max((q["estimated_ms"] for q in query_estimates), default=0)

        return {
            "total_estimated_ms": max_query_time,  # Parallel execution
            "query_estimates": query_estimates,
            "note": "These are rough heuristic estimates. Actual execution time varies.",
        }
