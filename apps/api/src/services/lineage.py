"""
Lineage Service - manages lineage graph for dashboards.
Tracks relationships: Dashboard → Chart → Query → Table

PDR Reference: §7 (Observability & Lineage), §11 (Acceptance Criteria)
"""

from typing import Any, Dict, List, Optional
from uuid import UUID

import structlog
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.cache import CacheInterface, build_lineage_cache_key
from src.core.config import settings
from src.core.exceptions import DashboardNotFoundException, LineageException
from src.models.db_models import Dashboard, EdgeType, LineageEdge, LineageNode, NodeType

logger = structlog.get_logger(__name__)


class LineageService:
    """
    Service for managing lineage graph.

    Lineage Structure (PDR §7):
    - Nodes: Dashboard, Chart, Query, Table
    - Edges: contains, executes, reads_from

    Example graph:
    Dashboard "revenue-dashboard"
      contains → Chart "chart_1"
        executes → Query "revenue_by_region"
          reads_from → Table "project.dataset.sales"

    PDR §11 Acceptance: "Lineage endpoint returns graph JSON for existing dashboard"
    """

    def __init__(self, db: AsyncSession, cache: Optional[CacheInterface] = None):
        """
        Initialize lineage service.

        Args:
            db: Database session
            cache: Optional cache for lineage queries
        """
        self.db = db
        self.cache = cache

    async def build_lineage_for_dashboard(
        self,
        slug: str,
        lineage_seeds: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Build lineage graph from compilation seeds.

        Called after dashboard compilation to populate lineage tables.

        Args:
            slug: Dashboard slug
            lineage_seeds: Seeds from CompilerService (nodes and edges)

        Returns:
            Dict with created node/edge counts
        """
        logger.info(
            "🔗 building_lineage_graph",
            slug=slug,
            node_count=len(lineage_seeds.get("nodes", [])),
            edge_count=len(lineage_seeds.get("edges", [])),
        )

        # Clear existing lineage for this dashboard
        await self._clear_dashboard_lineage(slug)

        nodes_created = 0
        edges_created = 0

        # Create nodes
        node_map: Dict[str, UUID] = {}  # Map node_id -> UUID

        for node_seed in lineage_seeds.get("nodes", []):
            node = await self._create_or_update_node(
                node_type=NodeType[node_seed["node_type"]],
                node_id=node_seed["node_id"],
                metadata=node_seed.get("metadata"),
            )
            node_map[node_seed["node_id"]] = node.id
            nodes_created += 1

        # Create edges
        for edge_seed in lineage_seeds.get("edges", []):
            source_uuid = node_map.get(edge_seed["source_node_id"])
            target_uuid = node_map.get(edge_seed["target_node_id"])

            if not source_uuid or not target_uuid:
                logger.warning(
                    "⚠️ lineage_edge_skipped_missing_node",
                    source=edge_seed["source_node_id"],
                    target=edge_seed["target_node_id"],
                )
                continue

            await self._create_edge(
                source_node_id=source_uuid,
                target_node_id=target_uuid,
                edge_type=EdgeType[edge_seed["edge_type"]],
                metadata=edge_seed.get("edge_metadata"),
            )
            edges_created += 1

        await self.db.flush()

        # Invalidate cache
        if self.cache:
            cache_key = build_lineage_cache_key(slug)
            await self.cache.delete(cache_key)

        logger.info(
            "✅ lineage_graph_built",
            slug=slug,
            nodes_created=nodes_created,
            edges_created=edges_created,
        )

        return {
            "dashboard_slug": slug,
            "nodes_created": nodes_created,
            "edges_created": edges_created,
        }

    async def get_lineage_graph(self, slug: str) -> Dict[str, Any]:
        """
        Get lineage graph for a dashboard in JSON format.

        Returns nodes and edges suitable for frontend visualization.

        Args:
            slug: Dashboard slug

        Returns:
            Dict with nodes and edges arrays

        Raises:
            DashboardNotFoundException: If dashboard not found
        """
        logger.info("📊 fetching_lineage_graph", slug=slug)

        # Check cache
        if self.cache:
            cache_key = build_lineage_cache_key(slug)
            cached = await self.cache.get(cache_key)
            if cached:
                logger.info("✅ lineage_cache_hit", slug=slug)
                return cached

        # Verify dashboard exists
        await self._verify_dashboard_exists(slug)

        # Fetch all nodes for this dashboard
        nodes = await self._get_dashboard_nodes(slug)

        # Fetch all edges for these nodes
        node_ids = [node.id for node in nodes]
        edges = await self._get_edges_for_nodes(node_ids)

        # Build JSON response
        lineage_graph = {
            "dashboard_slug": slug,
            "nodes": [
                {
                    "id": str(node.id),
                    "type": node.node_type.value,
                    "node_id": node.node_id,
                    "metadata": node.node_metadata or {},
                }
                for node in nodes
            ],
            "edges": [
                {
                    "id": str(edge.id),
                    "source": str(edge.source_node_id),
                    "target": str(edge.target_node_id),
                    "type": edge.edge_type.value,
                    "metadata": edge.edge_metadata or {},
                }
                for edge in edges
            ],
            "node_count": len(nodes),
            "edge_count": len(edges),
        }

        # Cache result
        if self.cache:
            await self.cache.set(
                key=cache_key,
                value=lineage_graph,
                ttl=settings.lineage_cache_ttl,
            )

        logger.info(
            "✅ lineage_graph_fetched",
            slug=slug,
            nodes=len(nodes),
            edges=len(edges),
        )

        return lineage_graph

    async def get_upstream_tables(self, slug: str) -> List[str]:
        """
        Get list of upstream tables that a dashboard depends on.

        Args:
            slug: Dashboard slug

        Returns:
            List of fully-qualified table names
        """
        logger.info("🔍 fetching_upstream_tables", slug=slug)

        # Get all table nodes connected to this dashboard
        nodes = await self._get_dashboard_nodes(slug)

        table_nodes = [
            node for node in nodes if node.node_type == NodeType.table
        ]

        tables = [node.node_id for node in table_nodes]

        logger.info(
            "✅ upstream_tables_fetched",
            slug=slug,
            table_count=len(tables),
        )

        return tables

    async def get_downstream_dashboards(self, table_name: str) -> List[str]:
        """
        Get list of dashboards that depend on a specific table.

        Useful for impact analysis: "If I change this table, which dashboards are affected?"

        Args:
            table_name: Fully-qualified table name

        Returns:
            List of dashboard slugs
        """
        logger.info("🔍 fetching_downstream_dashboards", table=table_name)

        # Find table node
        stmt = select(LineageNode).where(
            LineageNode.node_type == NodeType.table,
            LineageNode.node_id == table_name,
        )
        result = await self.db.execute(stmt)
        table_node = result.scalar_one_or_none()

        if not table_node:
            logger.info("⚠️ table_not_found_in_lineage", table=table_name)
            return []

        # Find all query nodes that read from this table
        query_edges_stmt = select(LineageEdge).where(
            LineageEdge.target_node_id == table_node.id,
            LineageEdge.edge_type == EdgeType.reads_from,
        )
        result = await self.db.execute(query_edges_stmt)
        query_edges = result.scalars().all()

        query_node_ids = [edge.source_node_id for edge in query_edges]

        if not query_node_ids:
            return []

        # Find all chart nodes that execute these queries
        chart_edges_stmt = select(LineageEdge).where(
            LineageEdge.target_node_id.in_(query_node_ids),
            LineageEdge.edge_type == EdgeType.executes,
        )
        result = await self.db.execute(chart_edges_stmt)
        chart_edges = result.scalars().all()

        chart_node_ids = [edge.source_node_id for edge in chart_edges]

        if not chart_node_ids:
            return []

        # Find all dashboard nodes that contain these charts
        dashboard_edges_stmt = select(LineageEdge).where(
            LineageEdge.target_node_id.in_(chart_node_ids),
            LineageEdge.edge_type == EdgeType.contains,
        )
        result = await self.db.execute(dashboard_edges_stmt)
        dashboard_edges = result.scalars().all()

        dashboard_node_ids = [edge.source_node_id for edge in dashboard_edges]

        # Get dashboard slugs
        dashboard_nodes_stmt = select(LineageNode).where(
            LineageNode.id.in_(dashboard_node_ids),
            LineageNode.node_type == NodeType.dashboard,
        )
        result = await self.db.execute(dashboard_nodes_stmt)
        dashboard_nodes = result.scalars().all()

        dashboard_slugs = [node.node_id for node in dashboard_nodes]

        logger.info(
            "✅ downstream_dashboards_fetched",
            table=table_name,
            dashboard_count=len(dashboard_slugs),
        )

        return dashboard_slugs

    async def _clear_dashboard_lineage(self, slug: str) -> None:
        """
        Clear all lineage nodes/edges for a dashboard.

        Args:
            slug: Dashboard slug
        """
        # Find dashboard node
        stmt = select(LineageNode).where(
            LineageNode.node_type == NodeType.dashboard,
            LineageNode.node_id == slug,
        )
        result = await self.db.execute(stmt)
        dashboard_node = result.scalar_one_or_none()

        if dashboard_node:
            # Delete dashboard node (cascade will delete edges and related nodes)
            await self.db.delete(dashboard_node)
            await self.db.flush()

            logger.info("🗑️ dashboard_lineage_cleared", slug=slug)

    async def _create_or_update_node(
        self,
        node_type: NodeType,
        node_id: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> LineageNode:
        """
        Create or update a lineage node.

        Args:
            node_type: Node type
            node_id: Node identifier
            metadata: Node metadata

        Returns:
            LineageNode
        """
        # Check if node exists
        stmt = select(LineageNode).where(
            LineageNode.node_type == node_type,
            LineageNode.node_id == node_id,
        )
        result = await self.db.execute(stmt)
        node = result.scalar_one_or_none()

        if node:
            # Update existing
            node.node_metadata = metadata
            node.updated_at = datetime.utcnow()
        else:
            # Create new
            from datetime import datetime
            node = LineageNode(
                node_type=node_type,
                node_id=node_id,
                node_metadata=metadata,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            self.db.add(node)

        await self.db.flush()
        return node

    async def _create_edge(
        self,
        source_node_id: UUID,
        target_node_id: UUID,
        edge_type: EdgeType,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> LineageEdge:
        """
        Create a lineage edge.

        Args:
            source_node_id: Source node UUID
            target_node_id: Target node UUID
            edge_type: Edge type
            metadata: Edge metadata

        Returns:
            LineageEdge
        """
        from datetime import datetime
        edge = LineageEdge(
            source_node_id=source_node_id,
            target_node_id=target_node_id,
            edge_type=edge_type,
            edge_metadata=metadata,
            created_at=datetime.utcnow(),
        )
        self.db.add(edge)
        await self.db.flush()
        return edge

    async def _get_dashboard_nodes(self, slug: str) -> List[LineageNode]:
        """
        Get all lineage nodes for a dashboard.

        Args:
            slug: Dashboard slug

        Returns:
            List of LineageNode
        """
        # Find dashboard node
        dashboard_stmt = select(LineageNode).where(
            LineageNode.node_type == NodeType.dashboard,
            LineageNode.node_id == slug,
        )
        result = await self.db.execute(dashboard_stmt)
        dashboard_node = result.scalar_one_or_none()

        if not dashboard_node:
            return []

        # Get all connected nodes (traversing edges)
        # For simplicity, we'll use a pattern match on node_id starting with slug
        stmt = select(LineageNode).where(
            or_(
                LineageNode.node_id == slug,
                LineageNode.node_id.like(f"{slug}:%"),
            )
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def _get_edges_for_nodes(self, node_ids: List[UUID]) -> List[LineageEdge]:
        """
        Get all edges connecting the given nodes.

        Args:
            node_ids: List of node UUIDs

        Returns:
            List of LineageEdge
        """
        if not node_ids:
            return []

        stmt = select(LineageEdge).where(
            or_(
                LineageEdge.source_node_id.in_(node_ids),
                LineageEdge.target_node_id.in_(node_ids),
            )
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def _verify_dashboard_exists(self, slug: str) -> None:
        """
        Verify dashboard exists in database.

        Args:
            slug: Dashboard slug

        Raises:
            DashboardNotFoundException: If not found
        """
        stmt = select(Dashboard).where(Dashboard.slug == slug)
        result = await self.db.execute(stmt)
        dashboard = result.scalar_one_or_none()

        if not dashboard:
            raise DashboardNotFoundException(slug=slug)
