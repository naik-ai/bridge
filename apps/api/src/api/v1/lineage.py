"""
Lineage endpoint for Peter Dashboard Platform.
Handles lineage graph retrieval for dashboards.

PDR Reference: §7 (Observability & Lineage), §11 (Acceptance Criteria)
"""

from typing import Optional

import structlog
from fastapi import APIRouter, Depends, Query

from src.core.dependencies import get_current_user, get_lineage_service
from src.core.exceptions import DashboardNotFoundException, LineageException
from src.core.response import ErrorCode, ResponseFactory
from src.models.db_models import User
from src.services.lineage import LineageService

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/lineage", tags=["Lineage"])


# =============================================================================
# Endpoints
# =============================================================================


@router.get("/{slug}")
async def get_dashboard_lineage(
    slug: str,
    include_upstream: bool = Query(False, description="Include upstream dependencies"),
    include_downstream: bool = Query(False, description="Include downstream usage"),
    lineage_service: LineageService = Depends(get_lineage_service),
    user: User = Depends(get_current_user),
) -> dict:
    """
    Get lineage graph for dashboard.

    PDR §7: "Lineage Tracking - Lineage graph built during dashboard compilation.
             Nodes represent: dashboards, charts, queries, BigQuery tables, BigQuery views.
             Edges represent: dashboard contains chart, chart executes query, query reads from table.
             Stored as simple node and edge tables in Postgres.
             API endpoint exposes graph in JSON format for frontend consumption."

    PDR §11 Acceptance: "Lineage endpoint returns graph JSON for existing dashboard"

    Lineage structure:
    - Nodes: {id, type, node_id, metadata}
    - Edges: {source, target, edge_type}

    Example graph:
    ```
    Dashboard "revenue-dashboard"
      contains → Chart "chart_1"
        executes → Query "revenue_by_region"
          reads_from → Table "project.dataset.sales"
    ```

    Args:
        slug: Dashboard slug
        include_upstream: Include upstream dependencies (tables → queries → dashboards)
        include_downstream: Include downstream usage (dashboards using this as source)
        lineage_service: Lineage service
        user: Current authenticated user

    Returns:
        Lineage graph with nodes and edges
    """
    try:
        logger.info(
            "lineage_requested",
            slug=slug,
            user_id=str(user.id),
            include_upstream=include_upstream,
            include_downstream=include_downstream,
        )

        # Get full lineage graph (filtering by upstream/downstream not yet implemented)
        graph = await lineage_service.get_lineage_graph(slug=slug)

        logger.info(
            "lineage_retrieved",
            slug=slug,
            nodes=len(graph.get("nodes", [])),
            edges=len(graph.get("edges", [])),
        )

        return ResponseFactory.success(data=graph)

    except DashboardNotFoundException as e:
        logger.warning("dashboard_not_found", slug=slug)
        return ResponseFactory.not_found_error(resource_type="dashboard", identifier=slug)

    except LineageException as e:
        logger.error("lineage_retrieval_failed", slug=slug, error=str(e))
        return ResponseFactory.error(
            error_code=ErrorCode.INTERNAL_SERVER_ERROR,
            message=str(e),
            details=e.details,
            status_code=500,
        )

    except Exception as e:
        logger.error("lineage_error", slug=slug, error=str(e))
        return ResponseFactory.error(
            error_code=ErrorCode.INTERNAL_SERVER_ERROR,
            message=f"Failed to retrieve lineage: {str(e)}",
            status_code=500,
        )
