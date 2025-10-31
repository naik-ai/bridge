"""
Schema Service - manages BigQuery schema metadata with caching layer.
Provides cached access to datasets, tables, and schema information.

Implements:
- Dataset listing with Redis cache
- Table listing with per-dataset caching
- Schema retrieval with granular caching
- Pattern-based cache invalidation
"""

from typing import Any

import structlog

from src.core.cache import CacheInterface
from src.integrations.bigquery_client import BigQueryClient

logger = structlog.get_logger(__name__)


class SchemaService:
    """
    Service for retrieving BigQuery schema metadata with caching.

    Features:
    - Cached dataset listing (1 hour TTL)
    - Cached table listing per dataset (15 minute TTL)
    - Cached schema retrieval per table (15 minute TTL)
    - Pattern-based cache invalidation
    - Force refresh support for all operations
    """

    # Cache TTL constants
    DATASET_TTL = 3600  # 1 hour
    TABLE_TTL = 900  # 15 minutes
    SCHEMA_TTL = 900  # 15 minutes

    def __init__(self, bq_client: BigQueryClient, cache: CacheInterface):
        """
        Initialize schema service.

        Args:
            bq_client: BigQuery client for schema operations
            cache: Cache interface for storing metadata
        """
        self.bq_client = bq_client
        self.cache = cache

        logger.info(
            "schema_service_initialized",
            dataset_ttl=self.DATASET_TTL,
            table_ttl=self.TABLE_TTL,
            schema_ttl=self.SCHEMA_TTL,
        )

    async def list_datasets(self, force_refresh: bool = False) -> list[dict[str, Any]]:
        """
        List all datasets in the project with caching.

        Args:
            force_refresh: If True, bypass cache and fetch fresh data

        Returns:
            List of dicts with dataset metadata:
            - dataset_id: Dataset name
            - location: Geographic location
            - creation_time: When dataset was created
            - description: Dataset description (if available)

        Raises:
            Exception: If BigQuery query fails
        """
        cache_key = "bigquery:datasets"

        # Check cache first (unless force refresh)
        if not force_refresh:
            cached_data = await self.cache.get(cache_key)
            if cached_data:
                logger.info("✅ cache_hit_datasets")
                return cached_data

        # Cache miss - fetch from BigQuery
        logger.info("🔄 fetching_datasets_from_bigquery")

        try:
            datasets = await self.bq_client.list_datasets()

            logger.info("✅ datasets_fetched", count=len(datasets))

            # Store in cache
            await self.cache.set(
                key=cache_key,
                value=datasets,
                ttl=self.DATASET_TTL,
            )

            logger.info("💾 datasets_cached", ttl=self.DATASET_TTL)

            return datasets

        except Exception as e:
            logger.error(
                "❌ list_datasets_failed",
                error=str(e),
            )
            raise

    async def list_tables(
        self,
        dataset_id: str,
        table_type: str | None = None,
        force_refresh: bool = False,
    ) -> list[dict[str, Any]]:
        """
        List tables in a dataset with caching.

        Args:
            dataset_id: Dataset name to query
            table_type: Optional filter for table type (BASE TABLE, VIEW, MATERIALIZED VIEW)
            force_refresh: If True, bypass cache and fetch fresh data

        Returns:
            List of dicts with table metadata:
            - table_name: Table name
            - table_type: Type of table (BASE TABLE, VIEW, etc.)
            - row_count: Approximate number of rows
            - size_bytes: Table size in bytes
            - creation_time: When table was created

        Raises:
            Exception: If BigQuery query fails
        """
        cache_key = f"bigquery:tables:{dataset_id}:{table_type or 'all'}"

        # Check cache first (unless force refresh)
        if not force_refresh:
            cached_data = await self.cache.get(cache_key)
            if cached_data:
                logger.info(
                    "✅ cache_hit_tables",
                    dataset=dataset_id,
                    table_type=table_type,
                )
                return cached_data

        # Cache miss - fetch from BigQuery
        logger.info(
            "🔄 fetching_tables_from_bigquery",
            dataset=dataset_id,
            table_type=table_type,
        )

        try:
            tables = await self.bq_client.list_tables(
                dataset_id=dataset_id,
                table_type=table_type,
            )

            logger.info(
                "✅ tables_fetched",
                dataset=dataset_id,
                count=len(tables),
            )

            # Store in cache
            await self.cache.set(
                key=cache_key,
                value=tables,
                ttl=self.TABLE_TTL,
            )

            logger.info(
                "💾 tables_cached",
                dataset=dataset_id,
                ttl=self.TABLE_TTL,
            )

            return tables

        except Exception as e:
            logger.error(
                "❌ list_tables_failed",
                dataset=dataset_id,
                table_type=table_type,
                error=str(e),
            )
            raise

    async def get_table_schema(
        self,
        dataset_id: str,
        table_name: str,
        force_refresh: bool = False,
    ) -> dict[str, Any]:
        """
        Get detailed schema for a table with caching.

        Args:
            dataset_id: Dataset name
            table_name: Table name
            force_refresh: If True, bypass cache and fetch fresh data

        Returns:
            Dict with schema metadata:
            - table_name: Table name
            - dataset_id: Dataset name
            - columns: List of column dicts with:
                - name: Column name
                - type: Data type
                - mode: NULLABLE or REQUIRED
                - ordinal_position: Column position
            - partitioning_info: Partitioning details (if available)
            - clustering_fields: Clustering fields (if available)

        Raises:
            Exception: If BigQuery query fails
        """
        cache_key = f"bigquery:schema:{dataset_id}:{table_name}"

        # Check cache first (unless force refresh)
        if not force_refresh:
            cached_data = await self.cache.get(cache_key)
            if cached_data:
                logger.info(
                    "✅ cache_hit_schema",
                    dataset=dataset_id,
                    table=table_name,
                )
                return cached_data

        # Cache miss - fetch from BigQuery
        logger.info(
            "🔄 fetching_schema_from_bigquery",
            dataset=dataset_id,
            table=table_name,
        )

        try:
            schema = await self.bq_client.get_table_schema(
                dataset_id=dataset_id,
                table_name=table_name,
            )

            logger.info(
                "✅ schema_fetched",
                dataset=dataset_id,
                table=table_name,
                column_count=len(schema.get("columns", [])),
            )

            # Store in cache
            await self.cache.set(
                key=cache_key,
                value=schema,
                ttl=self.SCHEMA_TTL,
            )

            logger.info(
                "💾 schema_cached",
                dataset=dataset_id,
                table=table_name,
                ttl=self.SCHEMA_TTL,
            )

            return schema

        except Exception as e:
            logger.error(
                "❌ get_table_schema_failed",
                dataset=dataset_id,
                table=table_name,
                error=str(e),
            )
            raise

    async def preview_table(
        self,
        dataset_id: str,
        table_name: str,
        limit: int = 50,
        page_token: str | None = None,
    ) -> dict[str, Any]:
        """
        Preview table data with pagination (NEVER cached - always fresh).

        This method fetches live data from BigQuery using the FREE tabledata.list API.
        Preview data is intentionally not cached to ensure users always see current data.

        Args:
            dataset_id: Dataset name
            table_name: Table name
            limit: Number of rows per page (min=1, max=1000, default=50)
            page_token: Pagination cursor (optional)

        Returns:
            Dict with preview data:
            {
                "rows": List[Dict],  # Data rows
                "schema": List[{"name": str, "type": str}],  # Column definitions
                "totalRows": int,  # Total rows in table
                "fetchedRows": int,  # Rows in this page
                "pageInfo": {
                    "nextPageToken": str | None,
                    "hasNextPage": bool
                },
                "metadata": {
                    "cost": 0.0,
                    "apiUsed": "tabledata.list"
                }
            }

        Raises:
            ValueError: If limit is invalid or page token is invalid
            Exception: If BigQuery API call fails
        """
        # Validate limit parameter
        if limit < 1:
            raise ValueError("limit must be at least 1")
        if limit > 1000:
            raise ValueError("limit cannot exceed 1000")

        logger.info(
            "📊 previewing_table",
            table=f"{dataset_id}.{table_name}",
            limit=limit,
            page_token=page_token[:50] if page_token else None,
        )

        try:
            # Fetch preview data from BigQuery (NEVER cached)
            preview_data = await self.bq_client.preview_table_data(
                dataset_id=dataset_id,
                table_name=table_name,
                max_results=limit,
                page_token=page_token,
            )

            logger.info(
                "✅ preview_fetched",
                table=f"{dataset_id}.{table_name}",
                rows=len(preview_data["rows"]),
                has_more=preview_data["pageInfo"]["hasNextPage"],
            )

            return preview_data

        except Exception as e:
            logger.error(
                "❌ preview_table_failed",
                table=f"{dataset_id}.{table_name}",
                limit=limit,
                error=str(e),
            )
            raise

    async def get_preview_stats(
        self,
        dataset_id: str,
        table_name: str,
    ) -> dict[str, Any]:
        """
        Get statistics for table preview operations (uses cached metadata).

        This method retrieves table metadata and calculates pagination statistics.
        It uses cached metadata from get_table_metadata to avoid unnecessary queries.

        Args:
            dataset_id: Dataset name
            table_name: Table name

        Returns:
            Dict with preview statistics:
            {
                "totalRows": int,  # Total rows in table
                "sizeBytes": int,  # Table size in bytes
                "isPartitioned": bool,  # Whether table is partitioned
                "estimatedPages": int,  # Estimated number of pages (totalRows / 50)
                "defaultPageSize": 50  # Default page size for preview
            }

        Raises:
            Exception: If metadata retrieval fails
        """
        logger.info(
            "📊 retrieving_preview_stats",
            table=f"{dataset_id}.{table_name}",
        )

        try:
            # Get table metadata (this method uses caching)
            metadata = await self.bq_client.get_table_metadata(
                dataset_id=dataset_id,
                table_name=table_name,
            )

            # Calculate estimated pages (using default page size of 50)
            default_page_size = 50
            total_rows = metadata["row_count"]
            estimated_pages = (total_rows + default_page_size - 1) // default_page_size  # Ceiling division

            stats = {
                "totalRows": total_rows,
                "sizeBytes": metadata["size_bytes"],
                "isPartitioned": metadata["is_partitioned"],
                "estimatedPages": estimated_pages,
                "defaultPageSize": default_page_size,
            }

            logger.info(
                "✅ preview_stats_retrieved",
                table=f"{dataset_id}.{table_name}",
                total_rows=total_rows,
                estimated_pages=estimated_pages,
            )

            return stats

        except Exception as e:
            logger.error(
                "❌ get_preview_stats_failed",
                table=f"{dataset_id}.{table_name}",
                error=str(e),
            )
            raise

    async def invalidate_cache(self, dataset_id: str | None = None) -> int:
        """
        Invalidate cache entries for schema metadata.

        Args:
            dataset_id: Optional dataset ID to limit invalidation scope.
                       If None, invalidates all schema cache entries.
                       If provided, invalidates all entries related to that dataset.

        Returns:
            Number of cache entries invalidated

        Raises:
            Exception: If cache invalidation fails
        """
        # Build pattern based on dataset_id
        if dataset_id:
            pattern = f"bigquery:*:{dataset_id}:*"
        else:
            pattern = "bigquery:*"

        logger.info(
            "🗑️ invalidating_schema_cache",
            dataset=dataset_id,
            pattern=pattern,
        )

        try:
            count = await self.cache.invalidate_pattern(pattern)

            logger.info(
                "✅ schema_cache_invalidated",
                dataset=dataset_id,
                count=count,
            )

            return count

        except Exception as e:
            logger.error(
                "❌ cache_invalidation_failed",
                dataset=dataset_id,
                pattern=pattern,
                error=str(e),
            )
            raise
