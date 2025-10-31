"""
Schema API - BigQuery schema browsing endpoints.

Provides endpoints for:
- Listing datasets
- Listing tables within datasets
- Retrieving table schemas
- Getting table metadata
- Previewing table data
- Cache invalidation

All endpoints use cost-optimized BigQuery APIs with aggressive caching.
"""

from typing import Optional

import structlog
from fastapi import APIRouter, Depends, Query

from src.core.dependencies import get_current_user, get_schema_service
from src.core.response import ErrorCode, ResponseFactory
from src.integrations.bigquery_client import BigQueryClient, get_bigquery_client
from src.models.db_models import User
from src.services.schema import SchemaService

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/schema", tags=["schema"])


# =============================================================================
# Endpoints
# =============================================================================


@router.get("/datasets")
async def list_datasets(
    force_refresh: bool = Query(False, description="Force cache refresh"),
    schema_service: SchemaService = Depends(get_schema_service),
    user: User = Depends(get_current_user),
) -> dict:
    """
    List all BigQuery datasets in the project.

    Uses INFORMATION_SCHEMA for metadata (0 bytes scanned, FREE).
    Results are cached for 1 hour unless force_refresh is True.

    Args:
        force_refresh: Bypass cache and fetch fresh data
        schema_service: Schema service instance
        user: Current authenticated user

    Returns:
        List of datasets with metadata:
        - dataset_id: Dataset name
        - location: Geographic location
        - creation_time: When dataset was created
        - description: Dataset description (if available)
    """
    try:
        logger.info("datasets_requested", user_id=str(user.id), force_refresh=force_refresh)

        datasets = await schema_service.list_datasets(force_refresh=force_refresh)

        logger.info("datasets_returned", user_id=str(user.id), count=len(datasets))

        return ResponseFactory.success(
            data={
                "datasets": datasets,
                "count": len(datasets),
            }
        )

    except Exception as e:
        logger.error("datasets_fetch_failed", user_id=str(user.id), error=str(e))
        return ResponseFactory.error(
            error_code=ErrorCode.BIGQUERY_ERROR,
            message=f"Failed to fetch datasets: {str(e)}",
            status_code=500,
        )


@router.get("/datasets/{dataset_id}/tables")
async def list_tables(
    dataset_id: str,
    table_type: Optional[str] = Query(None, description="Filter by table type (BASE TABLE, VIEW, MATERIALIZED VIEW)"),
    force_refresh: bool = Query(False, description="Force cache refresh"),
    schema_service: SchemaService = Depends(get_schema_service),
    user: User = Depends(get_current_user),
) -> dict:
    """
    List all tables in a dataset.

    Uses INFORMATION_SCHEMA for metadata (0 bytes scanned, FREE).
    Results are cached for 15 minutes unless force_refresh is True.

    Args:
        dataset_id: Dataset name to query
        table_type: Optional filter for table type (BASE TABLE, VIEW, MATERIALIZED VIEW)
        force_refresh: Bypass cache and fetch fresh data
        schema_service: Schema service instance
        user: Current authenticated user

    Returns:
        List of tables with metadata:
        - table_name: Table name
        - table_type: Type of table (BASE TABLE, VIEW, etc.)
        - row_count: Approximate number of rows
        - size_bytes: Table size in bytes
        - creation_time: When table was created
    """
    try:
        logger.info(
            "tables_requested",
            user_id=str(user.id),
            dataset_id=dataset_id,
            table_type=table_type,
            force_refresh=force_refresh,
        )

        tables = await schema_service.list_tables(
            dataset_id=dataset_id,
            table_type=table_type,
            force_refresh=force_refresh,
        )

        logger.info(
            "tables_returned",
            user_id=str(user.id),
            dataset_id=dataset_id,
            count=len(tables),
        )

        return ResponseFactory.success(
            data={
                "tables": tables,
                "count": len(tables),
            }
        )

    except Exception as e:
        logger.error(
            "tables_fetch_failed",
            user_id=str(user.id),
            dataset_id=dataset_id,
            error=str(e),
        )
        return ResponseFactory.error(
            error_code=ErrorCode.BIGQUERY_ERROR,
            message=f"Failed to fetch tables: {str(e)}",
            status_code=500,
        )


@router.get("/tables/{dataset_id}.{table_name}/schema")
async def get_table_schema(
    dataset_id: str,
    table_name: str,
    force_refresh: bool = Query(False, description="Force cache refresh"),
    schema_service: SchemaService = Depends(get_schema_service),
    user: User = Depends(get_current_user),
) -> dict:
    """
    Get detailed schema for a table.

    Uses INFORMATION_SCHEMA for metadata (0 bytes scanned, FREE).
    Results are cached for 15 minutes unless force_refresh is True.

    Args:
        dataset_id: Dataset name
        table_name: Table name
        force_refresh: Bypass cache and fetch fresh data
        schema_service: Schema service instance
        user: Current authenticated user

    Returns:
        Schema metadata:
        - table_name: Table name
        - dataset_id: Dataset name
        - columns: List of column definitions with name, type, mode, ordinal_position
        - partitioning_info: Partitioning details (if available)
        - clustering_fields: Clustering fields (if available)
    """
    try:
        logger.info(
            "schema_requested",
            user_id=str(user.id),
            table=f"{dataset_id}.{table_name}",
            force_refresh=force_refresh,
        )

        schema = await schema_service.get_table_schema(
            dataset_id=dataset_id,
            table_name=table_name,
            force_refresh=force_refresh,
        )

        logger.info(
            "schema_returned",
            user_id=str(user.id),
            table=f"{dataset_id}.{table_name}",
            column_count=len(schema.get("columns", [])),
        )

        return ResponseFactory.success(data=schema)

    except Exception as e:
        logger.error(
            "schema_fetch_failed",
            user_id=str(user.id),
            table=f"{dataset_id}.{table_name}",
            error=str(e),
        )
        return ResponseFactory.error(
            error_code=ErrorCode.BIGQUERY_ERROR,
            message=f"Failed to fetch table schema: {str(e)}",
            status_code=500,
        )


@router.get("/tables/{dataset_id}.{table_name}/metadata")
async def get_table_metadata(
    dataset_id: str,
    table_name: str,
    bq_client: BigQueryClient = Depends(get_bigquery_client),
    user: User = Depends(get_current_user),
) -> dict:
    """
    Get metadata for a table.

    Uses INFORMATION_SCHEMA for metadata (0 bytes scanned, FREE).
    Returns table statistics like row count, size, partitioning info.

    Args:
        dataset_id: Dataset name
        table_name: Table name
        bq_client: BigQuery client instance
        user: Current authenticated user

    Returns:
        Table metadata:
        - row_count: Number of rows in table
        - size_bytes: Table size in bytes
        - is_partitioned: Whether table is partitioned
        - clustering_fields: Clustering fields (if available)
    """
    try:
        logger.info(
            "metadata_requested",
            user_id=str(user.id),
            table=f"{dataset_id}.{table_name}",
        )

        metadata = await bq_client.get_table_metadata(
            dataset_id=dataset_id,
            table_name=table_name,
        )

        logger.info(
            "metadata_returned",
            user_id=str(user.id),
            table=f"{dataset_id}.{table_name}",
            row_count=metadata.get("row_count"),
        )

        return ResponseFactory.success(data=metadata)

    except Exception as e:
        logger.error(
            "metadata_fetch_failed",
            user_id=str(user.id),
            table=f"{dataset_id}.{table_name}",
            error=str(e),
        )
        return ResponseFactory.error(
            error_code=ErrorCode.BIGQUERY_ERROR,
            message=f"Failed to fetch table metadata: {str(e)}",
            status_code=500,
        )


@router.get("/tables/{dataset_id}.{table_name}/preview")
async def preview_table(
    dataset_id: str,
    table_name: str,
    limit: int = Query(50, ge=1, le=1000, description="Number of rows to preview (1-1000)"),
    page_token: Optional[str] = Query(None, description="Pagination cursor for next page"),
    schema_service: SchemaService = Depends(get_schema_service),
    user: User = Depends(get_current_user),
) -> dict:
    """
    Preview table data with pagination.

    Uses FREE tabledata.list API (0 bytes scanned, $0.00 cost).
    Preview data is NEVER cached to ensure users see fresh data.

    Supports cursor-based pagination for efficient navigation through large tables.

    Args:
        dataset_id: Dataset name
        table_name: Table name
        limit: Number of rows per page (1-1000, default 50)
        page_token: Pagination cursor (optional)
        schema_service: Schema service instance
        user: Current authenticated user

    Returns:
        Preview data:
        - rows: List of data rows as dictionaries
        - schema: Column definitions (name, type)
        - totalRows: Total rows in table
        - fetchedRows: Rows in this page
        - pageInfo: Pagination metadata (nextPageToken, hasNextPage)
        - metadata: Cost information (always $0.00)
    """
    try:
        logger.info(
            "preview_requested",
            user_id=str(user.id),
            table=f"{dataset_id}.{table_name}",
            limit=limit,
            has_page_token=page_token is not None,
        )

        preview_data = await schema_service.preview_table(
            dataset_id=dataset_id,
            table_name=table_name,
            limit=limit,
            page_token=page_token,
        )

        logger.info(
            "preview_returned",
            user_id=str(user.id),
            table=f"{dataset_id}.{table_name}",
            rows_returned=len(preview_data.get("rows", [])),
            has_next_page=preview_data.get("pageInfo", {}).get("hasNextPage", False),
        )

        return ResponseFactory.success(data=preview_data)

    except ValueError as e:
        # Handle validation errors (invalid limit or page_token)
        logger.warning(
            "preview_validation_failed",
            user_id=str(user.id),
            table=f"{dataset_id}.{table_name}",
            error=str(e),
        )
        return ResponseFactory.error(
            error_code=ErrorCode.VALIDATION_ERROR,
            message=str(e),
            status_code=400,
        )

    except Exception as e:
        logger.error(
            "preview_fetch_failed",
            user_id=str(user.id),
            table=f"{dataset_id}.{table_name}",
            error=str(e),
        )
        return ResponseFactory.error(
            error_code=ErrorCode.BIGQUERY_ERROR,
            message=f"Failed to preview table: {str(e)}",
            status_code=500,
        )


@router.post("/cache/invalidate")
async def invalidate_cache(
    dataset_id: Optional[str] = Query(None, description="Optional dataset ID to limit invalidation scope"),
    schema_service: SchemaService = Depends(get_schema_service),
    user: User = Depends(get_current_user),
) -> dict:
    """
    Invalidate schema cache entries.

    Clears cached metadata to force fresh data on next request.
    Can invalidate all entries or limit to a specific dataset.

    Args:
        dataset_id: Optional dataset ID to limit scope (None = invalidate all)
        schema_service: Schema service instance
        user: Current authenticated user

    Returns:
        Invalidation result:
        - count: Number of cache entries invalidated
        - scope: Invalidation scope (all or dataset-specific)
    """
    try:
        logger.info(
            "cache_invalidation_requested",
            user_id=str(user.id),
            dataset_id=dataset_id,
        )

        count = await schema_service.invalidate_cache(dataset_id=dataset_id)

        logger.info(
            "cache_invalidated",
            user_id=str(user.id),
            dataset_id=dataset_id,
            count=count,
        )

        return ResponseFactory.success(
            data={
                "count": count,
                "scope": f"dataset:{dataset_id}" if dataset_id else "all",
            }
        )

    except Exception as e:
        logger.error(
            "cache_invalidation_failed",
            user_id=str(user.id),
            dataset_id=dataset_id,
            error=str(e),
        )
        return ResponseFactory.error(
            error_code=ErrorCode.INTERNAL_SERVER_ERROR,
            message=f"Failed to invalidate cache: {str(e)}",
            status_code=500,
        )
