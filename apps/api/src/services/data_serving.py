"""
Data Serving Service - serves dashboard data from cache or executes queries.
Implements cache-first serving strategy with compact payloads.

PDR Reference: §4 (Data & Control Flows - Dashboard Data Serving), §5 (Caching & Freshness), §11 (Acceptance Criteria)
"""

from datetime import datetime
from typing import Any, Dict, Optional

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.cache import CacheInterface, build_dashboard_cache_key
from src.core.config import settings
from src.core.exceptions import DashboardNotFoundException
from src.integrations.bigquery_client import BigQueryClient
from src.models.db_models import Dashboard

logger = structlog.get_logger(__name__)


class DataServingService:
    """
    Service for serving dashboard data with cache-first strategy.

    Flow (PDR §4):
    1. Check cache for fresh results
    2. On cache miss: load YAML, compile, execute, transform, cache, return
    3. On cache hit: return cached payload (<300ms target)

    PDR §11 Acceptance:
    - "Data serving endpoint returns cached results in under 300ms on repeat request"
    - "Data serving endpoint executes queries on cache miss and populates cache"
    """

    def __init__(
        self,
        db: AsyncSession,
        cache: CacheInterface,
        bq_client: BigQueryClient,
    ):
        """
        Initialize data serving service.

        Args:
            db: Database session
            cache: Cache interface
            bq_client: BigQuery client
        """
        self.db = db
        self.cache = cache
        self.bq_client = bq_client

    async def serve_dashboard_data(
        self,
        slug: str,
        force_refresh: bool = False,
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get dashboard data (cache-first).

        Args:
            slug: Dashboard slug
            force_refresh: Force cache refresh
            user_id: User ID for logging

        Returns:
            Dict with dashboard data and metadata

        Raises:
            DashboardNotFoundException: If dashboard not found
        """
        logger.info(
            "📊 serving_dashboard_data",
            slug=slug,
            force_refresh=force_refresh,
        )

        # Load dashboard metadata from DB
        dashboard = await self._get_dashboard(slug)

        # Build cache keys for all queries
        # TODO: This requires loading YAML to get query list
        # For MVP, we'll implement basic caching
        # In production, we'd load the compiled execution plan

        cache_key = f"dashboard:{slug}:data:v{dashboard.version}"

        # Check cache (unless force refresh)
        if not force_refresh:
            cached_data = await self.cache.get(cache_key)
            if cached_data:
                logger.info(
                    "✅ cache_hit_dashboard_data",
                    slug=slug,
                    version=dashboard.version,
                )

                # Update last accessed timestamp
                dashboard.last_accessed = datetime.utcnow()
                dashboard.access_count += 1
                await self.db.flush()

                return {
                    "dashboard_slug": slug,
                    "version": dashboard.version,
                    "data": cached_data,
                    "cache_hit": True,
                    "as_of": cached_data.get("computed_at"),
                    "metadata": {
                        "name": dashboard.name,
                        "view_type": dashboard.view_type.value,
                    },
                }

        logger.info(
            "🔄 cache_miss_executing_queries",
            slug=slug,
        )

        # Cache miss: Execute queries
        # TODO: Integrate with StorageService to load YAML
        # TODO: Integrate with CompilerService to get execution plan
        # TODO: Integrate with SQLExecutorService to execute queries

        # For MVP, return placeholder
        # This will be completed once StorageService is implemented
        computed_data = {
            "computed_at": datetime.utcnow().isoformat(),
            "charts": {},
            "query_count": 0,
            "note": "TODO: Implement query execution via StorageService + CompilerService + SQLExecutorService",
        }

        # Cache the result
        await self.cache.set(
            key=cache_key,
            value=computed_data,
            ttl=settings.cache_default_ttl,
        )

        # Update dashboard access stats
        dashboard.last_accessed = datetime.utcnow()
        dashboard.access_count += 1
        await self.db.flush()

        logger.info(
            "✅ dashboard_data_computed_and_cached",
            slug=slug,
            version=dashboard.version,
        )

        return {
            "dashboard_slug": slug,
            "version": dashboard.version,
            "data": computed_data,
            "cache_hit": False,
            "as_of": computed_data["computed_at"],
            "metadata": {
                "name": dashboard.name,
                "view_type": dashboard.view_type.value,
            },
        }

    async def get_chart_data(
        self,
        slug: str,
        chart_id: str,
        force_refresh: bool = False,
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get data for a specific chart (useful for partial updates).

        Args:
            slug: Dashboard slug
            chart_id: Chart ID
            force_refresh: Force cache refresh
            user_id: User ID for logging

        Returns:
            Dict with chart data

        Raises:
            DashboardNotFoundException: If dashboard not found
        """
        logger.info(
            "📈 serving_chart_data",
            slug=slug,
            chart_id=chart_id,
        )

        # Load dashboard
        dashboard = await self._get_dashboard(slug)

        # Build cache key for specific chart
        cache_key = f"dashboard:{slug}:chart:{chart_id}:v{dashboard.version}"

        # Check cache
        if not force_refresh:
            cached_data = await self.cache.get(cache_key)
            if cached_data:
                logger.info("✅ cache_hit_chart_data", slug=slug, chart_id=chart_id)
                return {
                    "chart_id": chart_id,
                    "data": cached_data,
                    "cache_hit": True,
                }

        # Cache miss: Execute query for this chart
        # TODO: Load YAML, find query for chart, execute, transform, cache
        logger.info("🔄 cache_miss_executing_chart_query", slug=slug, chart_id=chart_id)

        # Placeholder
        computed_data = {
            "computed_at": datetime.utcnow().isoformat(),
            "data": [],
            "note": "TODO: Implement chart-specific query execution",
        }

        # Cache the result
        await self.cache.set(
            key=cache_key,
            value=computed_data,
            ttl=settings.cache_default_ttl,
        )

        return {
            "chart_id": chart_id,
            "data": computed_data,
            "cache_hit": False,
        }

    async def invalidate_dashboard_cache(self, slug: str) -> int:
        """
        Invalidate all cache entries for a dashboard.

        Args:
            slug: Dashboard slug

        Returns:
            Number of cache entries invalidated
        """
        logger.info("🗑️ invalidating_dashboard_cache", slug=slug)

        pattern = f"dashboard:{slug}:*"
        count = await self.cache.invalidate_pattern(pattern)

        logger.info(
            "✅ dashboard_cache_invalidated",
            slug=slug,
            entries_cleared=count,
        )

        return count

    async def get_dashboard_freshness(self, slug: str) -> Dict[str, Any]:
        """
        Get freshness information for dashboard cache.

        Args:
            slug: Dashboard slug

        Returns:
            Dict with freshness metadata
        """
        dashboard = await self._get_dashboard(slug)
        cache_key = f"dashboard:{slug}:data:v{dashboard.version}"

        cached_data = await self.cache.get(cache_key)

        if not cached_data:
            return {
                "cached": False,
                "last_computed": None,
                "staleness_seconds": None,
            }

        computed_at_str = cached_data.get("computed_at")
        if computed_at_str:
            computed_at = datetime.fromisoformat(computed_at_str.replace("Z", "+00:00"))
            staleness = (datetime.utcnow() - computed_at).total_seconds()
        else:
            staleness = None

        return {
            "cached": True,
            "last_computed": computed_at_str,
            "staleness_seconds": staleness,
            "dashboard_version": dashboard.version,
            "last_accessed": (
                dashboard.last_accessed.isoformat() if dashboard.last_accessed else None
            ),
        }

    async def _get_dashboard(self, slug: str) -> Dashboard:
        """
        Get dashboard from database.

        Args:
            slug: Dashboard slug

        Returns:
            Dashboard model

        Raises:
            DashboardNotFoundException: If not found
        """
        stmt = select(Dashboard).where(Dashboard.slug == slug)
        result = await self.db.execute(stmt)
        dashboard = result.scalar_one_or_none()

        if not dashboard:
            raise DashboardNotFoundException(slug=slug)

        return dashboard

    async def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dict with cache stats
        """
        health = await self.cache.health_check()
        return {
            "cache_type": health.get("type"),
            "cache_status": health.get("status"),
            "cache_size": health.get("size"),
            "cache_max_size": health.get("max_size"),
        }

    # TODO: The following methods will be completed after StorageService,
    # CompilerService, and SQLExecutorService integration

    async def _load_and_execute_queries(
        self,
        slug: str,
        dashboard: Dashboard,
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Load YAML, compile, execute queries, and transform results.

        This will integrate:
        1. StorageService - load YAML
        2. CompilerService - compile to execution plan
        3. SQLExecutorService - execute queries
        4. Transform results to compact payloads

        Args:
            slug: Dashboard slug
            dashboard: Dashboard model
            user_id: User ID for logging

        Returns:
            Dict with computed chart data
        """
        # TODO: Implement after StorageService is ready
        raise NotImplementedError("Query execution not yet implemented")
