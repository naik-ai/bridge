"""
BigQuery client wrapper with guardrails and cost controls.
Enforces byte limits, result cache, and safe query execution.
"""

import hashlib
from typing import Any, Dict, List, Optional

import structlog
from google.cloud import bigquery
from google.cloud.bigquery import QueryJobConfig
from google.oauth2 import service_account

from src.core.config import settings
from src.core.secrets import get_bigquery_credentials

logger = structlog.get_logger(__name__)

# Dangerous SQL patterns to block
DANGEROUS_PATTERNS = [
    "DROP ",
    "DELETE ",
    "TRUNCATE ",
    "ALTER ",
    "CREATE ",
    "GRANT ",
    "REVOKE ",
    "INSERT ",
    "UPDATE ",
    "MERGE ",
]


class BigQueryClient:
    """
    BigQuery client with safety guardrails.

    Features:
    - Maximum bytes billed cap
    - Result cache enforcement
    - Query timeout
    - Dataset allowlist
    - Dangerous pattern detection
    - Sample result limiting
    """

    def __init__(self):
        """Initialize BigQuery client with credentials."""
        self._client: Optional[bigquery.Client] = None
        self._credentials_path = get_bigquery_credentials()

    @property
    def client(self) -> bigquery.Client:
        """Lazy-load BigQuery client."""
        if self._client is None:
            try:
                # Load credentials
                if self._credentials_path and self._credentials_path.endswith(".json"):
                    # Service account JSON file
                    credentials = service_account.Credentials.from_service_account_file(
                        self._credentials_path,
                        scopes=["https://www.googleapis.com/auth/bigquery"],
                    )
                    self._client = bigquery.Client(
                        credentials=credentials,
                        project=settings.gcp_project_id,
                        location=settings.bigquery_location,
                    )
                elif self._credentials_path:
                    # JSON string from Secret Manager
                    import json
                    import tempfile

                    # Write JSON to temp file
                    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
                        json.dump(json.loads(self._credentials_path), f)
                        temp_path = f.name

                    credentials = service_account.Credentials.from_service_account_file(
                        temp_path,
                        scopes=["https://www.googleapis.com/auth/bigquery"],
                    )
                    self._client = bigquery.Client(
                        credentials=credentials,
                        project=settings.gcp_project_id,
                        location=settings.bigquery_location,
                    )
                else:
                    # Use application default credentials
                    self._client = bigquery.Client(
                        project=settings.gcp_project_id,
                        location=settings.bigquery_location,
                    )

                logger.info(
                    "bigquery_client_initialized",
                    project=settings.gcp_project_id,
                    location=settings.bigquery_location,
                )
            except Exception as e:
                logger.error("bigquery_client_init_failed", error=str(e))
                raise

        return self._client

    @property
    def project_id(self) -> str:
        """Return GCP project ID for this client."""
        if self._client:
            return self._client.project
        return settings.gcp_project_id

    async def dry_run(self, sql: str) -> Dict[str, Any]:
        """
        Perform BigQuery dry run to validate query and estimate bytes.

        Args:
            sql: SQL query to validate

        Returns:
            Dict with validation result and estimated bytes
        """
        import asyncio

        def _sync_dry_run() -> Dict[str, Any]:
            """Sync wrapper for BigQuery dry run."""
            try:
                job_config = QueryJobConfig(dry_run=True)
                query_job = self.client.query(sql, job_config=job_config)

                logger.info(
                    "bigquery_dry_run_success",
                    estimated_bytes=query_job.total_bytes_processed or 0,
                )

                return {
                    "valid": True,
                    "estimated_bytes": query_job.total_bytes_processed or 0,
                }
            except Exception as e:
                logger.warning("bigquery_dry_run_failed", error=str(e))
                return {
                    "valid": False,
                    "error": str(e),
                }

        # Run sync operation in thread pool to avoid blocking event loop
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _sync_dry_run)

    def check_health(self) -> Dict[str, Any]:
        """
        Check BigQuery client health.

        Returns:
            Dict with health status
        """
        try:
            # Try to access the client (triggers initialization)
            project = self.project_id

            return {
                "status": "healthy",
                "project": project,
            }
        except Exception as e:
            logger.error("bigquery_health_check_failed", error=str(e))
            return {
                "status": "unhealthy",
                "error": str(e),
            }

    def validate_query(self, sql: str) -> tuple[bool, Optional[str]]:
        """
        Validate SQL for dangerous patterns.

        Args:
            sql: SQL query string

        Returns:
            Tuple of (is_valid, error_message)
        """
        sql_upper = sql.upper()

        # Check for dangerous patterns
        for pattern in DANGEROUS_PATTERNS:
            if pattern in sql_upper:
                return False, f"Dangerous SQL pattern detected: {pattern.strip()}"

        # Check if query references allowed datasets
        if settings.bigquery_allowed_datasets:
            # Simple check - looks for dataset references
            found_allowed = False
            for dataset in settings.bigquery_allowed_datasets:
                if f"{dataset}." in sql or f"`{dataset}." in sql:
                    found_allowed = True
                    break

            if not found_allowed and settings.bigquery_allowed_datasets:
                return (
                    False,
                    f"Query must reference one of allowed datasets: {', '.join(settings.bigquery_allowed_datasets)}",
                )

        return True, None

    async def execute_query(
        self,
        sql: str,
        parameters: Optional[Dict[str, Any]] = None,
        max_bytes_billed: Optional[int] = None,
        timeout: Optional[int] = None,
        use_cache: bool = True,
    ) -> bigquery.QueryJob:
        """
        Execute SQL query with guardrails (async).

        Args:
            sql: SQL query string
            parameters: Query parameters (for parameterized queries)
            max_bytes_billed: Maximum bytes to bill (default from settings)
            timeout: Query timeout in seconds (default from settings)
            use_cache: Whether to use BigQuery result cache

        Returns:
            QueryJob object

        Raises:
            ValueError: If query validation fails
            Exception: If query execution fails
        """
        import asyncio

        # Validate query
        is_valid, error = self.validate_query(sql)
        if not is_valid:
            logger.warning("query_validation_failed", error=error, sql_preview=sql[:100])
            raise ValueError(error)

        # Configure job
        job_config = QueryJobConfig(
            maximum_bytes_billed=max_bytes_billed or settings.bigquery_max_bytes_billed,
            use_query_cache=use_cache if settings.bigquery_use_query_cache else False,
        )

        # Add parameters if provided
        if parameters:
            job_config.query_parameters = [
                bigquery.ScalarQueryParameter(k, "STRING", v) for k, v in parameters.items()
            ]

        def _sync_execute() -> bigquery.QueryJob:
            """Sync wrapper for BigQuery query execution."""
            try:
                logger.info(
                    "executing_bigquery_query",
                    sql_hash=self.hash_query(sql),
                    max_bytes=job_config.maximum_bytes_billed,
                    use_cache=job_config.use_query_cache,
                )

                # Execute query
                query_job = self.client.query(sql, job_config=job_config)

                # Wait for completion with timeout
                query_job.result(timeout=timeout or settings.bigquery_query_timeout)

                logger.info(
                    "bigquery_query_completed",
                    job_id=query_job.job_id,
                    bytes_processed=query_job.total_bytes_processed,
                    bytes_billed=query_job.total_bytes_billed,
                    cache_hit=query_job.cache_hit,
                    duration_ms=query_job.ended - query_job.started
                    if query_job.ended and query_job.started
                    else None,
                )

                return query_job

            except Exception as e:
                logger.error(
                    "bigquery_query_failed",
                    error=str(e),
                    sql_hash=self.hash_query(sql),
                )
                raise

        # Run sync operation in thread pool to avoid blocking event loop
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _sync_execute)

    def get_query_metadata(self, job: bigquery.QueryJob) -> Dict[str, Any]:
        """
        Extract metadata from completed query job.

        Args:
            job: Completed QueryJob

        Returns:
            Dict with schema, row count, bytes scanned, etc.
        """
        schema = []
        if job.schema:
            schema = [{"name": field.name, "type": field.field_type} for field in job.schema]

        return {
            "job_id": job.job_id,
            "schema": schema,
            "row_count": job.result().total_rows,
            "bytes_scanned": job.total_bytes_processed or 0,
            "bytes_billed": job.total_bytes_billed or 0,
            "cache_hit": job.cache_hit or False,
            "duration_ms": (
                int((job.ended - job.started).total_seconds() * 1000)
                if job.ended and job.started
                else 0
            ),
        }

    def sample_results(self, job: bigquery.QueryJob, max_rows: int = 100) -> List[Dict[str, Any]]:
        """
        Get sample rows from query results.

        Args:
            job: Completed QueryJob
            max_rows: Maximum number of rows to return

        Returns:
            List of row dicts (limited to max_rows)
        """
        results = job.result(max_results=max_rows)
        rows = []

        for row in results:
            # Convert Row to dict
            row_dict = dict(row.items())
            # Convert datetime objects to ISO strings
            for key, value in row_dict.items():
                if hasattr(value, "isoformat"):
                    row_dict[key] = value.isoformat()
            rows.append(row_dict)

        return rows

    async def execute_for_verification(
        self,
        sql: str,
        parameters: Optional[Dict[str, Any]] = None,
        max_bytes_billed: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Execute query for LLM verification loop.
        Returns metadata + sample rows (max 100).

        Args:
            sql: SQL query
            parameters: Query parameters
            max_bytes_billed: Byte limit override

        Returns:
            Dict with metadata and sample rows
        """
        job = await self.execute_query(
            sql=sql,
            parameters=parameters,
            max_bytes_billed=max_bytes_billed,
            use_cache=True,
        )

        metadata = self.get_query_metadata(job)
        sample_rows = self.sample_results(job, max_rows=100)

        return {
            **metadata,
            "sample_rows": sample_rows,
        }

    async def execute_for_serving(
        self,
        sql: str,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Execute query for data serving.
        Returns all results (not limited).

        Args:
            sql: SQL query
            parameters: Query parameters

        Returns:
            List of all result rows
        """
        job = await self.execute_query(sql=sql, parameters=parameters, use_cache=True)

        # Get all results (not limited)
        results = job.result()
        rows = []

        for row in results:
            row_dict = dict(row.items())
            # Convert datetime objects to ISO strings
            for key, value in row_dict.items():
                if hasattr(value, "isoformat"):
                    row_dict[key] = value.isoformat()
            rows.append(row_dict)

        return rows

    async def list_datasets(self) -> List[Dict[str, Any]]:
        """
        List all datasets in the project using INFORMATION_SCHEMA.
        This query is FREE (scans 0 bytes).

        Returns:
            List of dicts with dataset metadata:
            - dataset_id: Dataset name
            - location: Geographic location
            - creation_time: When dataset was created
            - description: Dataset description (if available)

        Raises:
            Exception: If query execution fails
        """
        import asyncio

        def _sync_list_datasets() -> List[Dict[str, Any]]:
            """Sync wrapper for listing datasets."""
            try:
                # Use INFORMATION_SCHEMA to list datasets (FREE query)
                sql = f"""
                SELECT
                    schema_name as dataset_id,
                    location,
                    creation_time,
                    COALESCE(option_value, '') as description
                FROM
                    `{self.project_id}.INFORMATION_SCHEMA.SCHEMATA`
                LEFT JOIN
                    `{self.project_id}.INFORMATION_SCHEMA.SCHEMATA_OPTIONS`
                USING (schema_name)
                WHERE
                    option_name = 'description' OR option_name IS NULL
                ORDER BY
                    schema_name
                """

                job_config = QueryJobConfig(use_query_cache=True)
                query_job = self.client.query(sql, job_config=job_config)
                results = query_job.result()

                logger.info(
                    "list_datasets_success",
                    project=self.project_id,
                    bytes_scanned=query_job.total_bytes_processed or 0,
                    cache_hit=query_job.cache_hit,
                )

                datasets = []
                for row in results:
                    datasets.append({
                        "dataset_id": row.dataset_id,
                        "location": row.location,
                        "creation_time": row.creation_time.isoformat() if row.creation_time else None,
                        "description": row.description or "",
                    })

                return datasets

            except Exception as e:
                logger.error("list_datasets_failed", error=str(e), project=self.project_id)
                raise

        # Run sync operation in thread pool to avoid blocking event loop
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _sync_list_datasets)

    async def list_tables(
        self,
        dataset_id: str,
        table_type: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        List tables in a dataset using INFORMATION_SCHEMA.
        This query is FREE (scans 0 bytes).

        Args:
            dataset_id: Dataset name to query
            table_type: Optional filter for table type (BASE TABLE, VIEW, MATERIALIZED VIEW)

        Returns:
            List of dicts with table metadata:
            - table_name: Table name
            - table_type: Type of table (BASE TABLE, VIEW, etc.)
            - row_count: Approximate number of rows
            - size_bytes: Table size in bytes
            - creation_time: When table was created

        Raises:
            Exception: If query execution fails
        """
        import asyncio

        def _sync_list_tables() -> List[Dict[str, Any]]:
            """Sync wrapper for listing tables."""
            try:
                # Use INFORMATION_SCHEMA to list tables (FREE query)
                sql = f"""
                SELECT
                    table_name,
                    table_type,
                    COALESCE(row_count, 0) as row_count,
                    COALESCE(size_bytes, 0) as size_bytes,
                    creation_time
                FROM
                    `{self.project_id}.{dataset_id}.INFORMATION_SCHEMA.TABLES`
                """

                # Add table_type filter if provided
                if table_type:
                    sql += f"\nWHERE table_type = '{table_type}'"

                sql += "\nORDER BY table_name"

                job_config = QueryJobConfig(use_query_cache=True)
                query_job = self.client.query(sql, job_config=job_config)
                results = query_job.result()

                logger.info(
                    "list_tables_success",
                    dataset=dataset_id,
                    table_type_filter=table_type,
                    bytes_scanned=query_job.total_bytes_processed or 0,
                    cache_hit=query_job.cache_hit,
                )

                tables = []
                for row in results:
                    tables.append({
                        "table_name": row.table_name,
                        "table_type": row.table_type,
                        "row_count": row.row_count or 0,
                        "size_bytes": row.size_bytes or 0,
                        "creation_time": row.creation_time.isoformat() if row.creation_time else None,
                    })

                return tables

            except Exception as e:
                logger.error(
                    "list_tables_failed",
                    error=str(e),
                    dataset=dataset_id,
                    table_type_filter=table_type,
                )
                raise

        # Run sync operation in thread pool to avoid blocking event loop
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _sync_list_tables)

    async def get_table_schema(
        self,
        dataset_id: str,
        table_name: str,
    ) -> Dict[str, Any]:
        """
        Get detailed schema for a table using INFORMATION_SCHEMA.
        This query is FREE (scans 0 bytes).

        Args:
            dataset_id: Dataset name
            table_name: Table name

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
            Exception: If query execution fails
        """
        import asyncio

        def _sync_get_table_schema() -> Dict[str, Any]:
            """Sync wrapper for getting table schema."""
            try:
                # Query INFORMATION_SCHEMA for columns (FREE query)
                columns_sql = f"""
                SELECT
                    column_name,
                    data_type,
                    is_nullable,
                    ordinal_position
                FROM
                    `{self.project_id}.{dataset_id}.INFORMATION_SCHEMA.COLUMNS`
                WHERE
                    table_name = '{table_name}'
                ORDER BY
                    ordinal_position
                """

                # Query for partitioning and clustering info (FREE query)
                table_info_sql = f"""
                SELECT
                    t.table_name,
                    COALESCE(po.option_value, '') as partition_by,
                    COALESCE(co.option_value, '') as cluster_by
                FROM
                    `{self.project_id}.{dataset_id}.INFORMATION_SCHEMA.TABLES` t
                LEFT JOIN
                    `{self.project_id}.{dataset_id}.INFORMATION_SCHEMA.TABLE_OPTIONS` po
                ON
                    t.table_name = po.table_name AND po.option_name = 'partition_expiration_days'
                LEFT JOIN
                    `{self.project_id}.{dataset_id}.INFORMATION_SCHEMA.TABLE_OPTIONS` co
                ON
                    t.table_name = co.table_name AND co.option_name = 'clustering'
                WHERE
                    t.table_name = '{table_name}'
                LIMIT 1
                """

                job_config = QueryJobConfig(use_query_cache=True)

                # Get columns
                columns_job = self.client.query(columns_sql, job_config=job_config)
                columns_results = columns_job.result()

                columns = []
                for row in columns_results:
                    columns.append({
                        "name": row.column_name,
                        "type": row.data_type,
                        "mode": "REQUIRED" if row.is_nullable == "NO" else "NULLABLE",
                        "ordinal_position": row.ordinal_position,
                    })

                # Get partitioning/clustering info
                table_info_job = self.client.query(table_info_sql, job_config=job_config)
                table_info_results = table_info_job.result()

                partition_by = ""
                cluster_by = ""
                for row in table_info_results:
                    partition_by = row.partition_by or ""
                    cluster_by = row.cluster_by or ""
                    break

                logger.info(
                    "get_table_schema_success",
                    dataset=dataset_id,
                    table=table_name,
                    column_count=len(columns),
                    bytes_scanned=(columns_job.total_bytes_processed or 0) + (table_info_job.total_bytes_processed or 0),
                    cache_hit=columns_job.cache_hit and table_info_job.cache_hit,
                )

                return {
                    "table_name": table_name,
                    "dataset_id": dataset_id,
                    "columns": columns,
                    "partitioning_info": partition_by,
                    "clustering_fields": cluster_by,
                }

            except Exception as e:
                logger.error(
                    "get_table_schema_failed",
                    error=str(e),
                    dataset=dataset_id,
                    table=table_name,
                )
                raise

        # Run sync operation in thread pool to avoid blocking event loop
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _sync_get_table_schema)

    async def get_table_metadata(
        self,
        dataset_id: str,
        table_name: str,
    ) -> Dict[str, Any]:
        """
        Get metadata for a single table using INFORMATION_SCHEMA.
        This query is FREE (scans 0 bytes).

        Args:
            dataset_id: Dataset name
            table_name: Table name

        Returns:
            Dict with table metadata:
            - row_count: Number of rows
            - size_bytes: Table size in bytes
            - is_partitioned: Whether table is partitioned
            - clustering_fields: Clustering fields (if available)
            - creation_time: When table was created

        Raises:
            Exception: If query execution fails
        """
        import asyncio

        def _sync_get_table_metadata() -> Dict[str, Any]:
            """Sync wrapper for getting table metadata."""
            try:
                # Use INFORMATION_SCHEMA to get table metadata (FREE query)
                sql = f"""
                SELECT
                    t.table_name,
                    COALESCE(t.row_count, 0) as row_count,
                    COALESCE(t.size_bytes, 0) as size_bytes,
                    CASE WHEN t.is_partitioning_column = 'YES' THEN TRUE ELSE FALSE END as is_partitioned,
                    t.creation_time,
                    COALESCE(co.option_value, '') as clustering_fields
                FROM
                    `{self.project_id}.{dataset_id}.INFORMATION_SCHEMA.TABLES` t
                LEFT JOIN
                    `{self.project_id}.{dataset_id}.INFORMATION_SCHEMA.TABLE_OPTIONS` co
                ON
                    t.table_name = co.table_name AND co.option_name = 'clustering'
                WHERE
                    t.table_name = '{table_name}'
                LIMIT 1
                """

                job_config = QueryJobConfig(use_query_cache=True)
                query_job = self.client.query(sql, job_config=job_config)
                results = query_job.result()

                metadata = None
                for row in results:
                    metadata = {
                        "row_count": row.row_count or 0,
                        "size_bytes": row.size_bytes or 0,
                        "is_partitioned": row.is_partitioned or False,
                        "clustering_fields": row.clustering_fields or "",
                        "creation_time": row.creation_time.isoformat() if row.creation_time else None,
                    }
                    break

                if metadata is None:
                    raise ValueError(f"Table {dataset_id}.{table_name} not found")

                logger.info(
                    "get_table_metadata_success",
                    dataset=dataset_id,
                    table=table_name,
                    bytes_scanned=query_job.total_bytes_processed or 0,
                    cache_hit=query_job.cache_hit,
                )

                return metadata

            except Exception as e:
                logger.error(
                    "get_table_metadata_failed",
                    error=str(e),
                    dataset=dataset_id,
                    table=table_name,
                )
                raise

        # Run sync operation in thread pool to avoid blocking event loop
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _sync_get_table_metadata)

    def check_health(self) -> Dict[str, Any]:
        """
        Check BigQuery connectivity.

        Returns:
            Dict with health status
        """
        try:
            # Simple query to test connectivity
            job = self.client.query("SELECT 1 as test")
            job.result(timeout=5)

            return {
                "status": "healthy",
                "project": settings.gcp_project_id,
                "location": settings.bigquery_location,
            }
        except Exception as e:
            logger.error("bigquery_health_check_failed", error=str(e))
            return {
                "status": "unhealthy",
                "error": str(e),
            }

    def _serialize_row(self, row: bigquery.Row) -> Dict[str, Any]:
        """
        Convert BigQuery Row to serializable dict.
        Handles datetime serialization and nested fields.

        Args:
            row: BigQuery Row object

        Returns:
            Dict with serialized values
        """
        row_dict = dict(row.items())

        # Serialize datetime objects to ISO strings
        for key, value in row_dict.items():
            if value is None:
                # NULL values remain None
                continue
            elif hasattr(value, "isoformat"):
                # datetime, date, time objects
                row_dict[key] = value.isoformat()
            elif isinstance(value, (list, tuple)):
                # Repeated fields - recursively serialize
                row_dict[key] = [
                    item.isoformat() if hasattr(item, "isoformat") else item
                    for item in value
                ]
            elif isinstance(value, dict):
                # Nested fields - recursively serialize
                for nested_key, nested_value in value.items():
                    if hasattr(nested_value, "isoformat"):
                        value[nested_key] = nested_value.isoformat()
                row_dict[key] = value

        return row_dict

    async def preview_table_data(
        self,
        dataset_id: str,
        table_name: str,
        max_results: int = 50,
        page_token: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Preview table data using FREE tabledata.list API (cursor-based pagination).
        This operation costs $0.00 - it does NOT execute SQL queries.

        Args:
            dataset_id: Dataset name
            table_name: Table name
            max_results: Page size (default: 50, max: 1000)
            page_token: Cursor for pagination (optional)

        Returns:
            Dict with preview data:
            {
                "rows": List[Dict],  # Serialized rows
                "schema": List[{"name": str, "type": str}],  # Column definitions
                "totalRows": int,  # Total rows in table
                "fetchedRows": int,  # Rows in this page
                "pageInfo": {
                    "nextPageToken": str | None,
                    "hasNextPage": bool
                },
                "metadata": {
                    "cost": 0.0,  # Always 0 for tabledata.list
                    "apiUsed": "tabledata.list"
                }
            }

        Raises:
            Exception: If table not found or invalid page token
        """
        import asyncio

        def _sync_preview() -> Dict[str, Any]:
            """Sync wrapper for BigQuery list_rows operation."""
            try:
                # Construct table reference
                table_ref = f"{self.project_id}.{dataset_id}.{table_name}"

                logger.info(
                    "📊 previewing_table",
                    dataset=dataset_id,
                    table=table_name,
                    max_results=max_results,
                    page_token=page_token[:20] + "..." if page_token and len(page_token) > 20 else page_token,
                )

                # Get table metadata
                table = self.client.get_table(table_ref)

                # List rows using FREE tabledata.list API
                rows_iterator = self.client.list_rows(
                    table,
                    max_results=max_results,
                    page_token=page_token,
                )

                # Get the current page (not all results)
                page = next(rows_iterator.pages)

                # Serialize rows
                rows = [self._serialize_row(row) for row in page]

                # Extract schema
                schema = [
                    {"name": field.name, "type": field.field_type}
                    for field in table.schema
                ]

                # Build response
                result = {
                    "rows": rows,
                    "schema": schema,
                    "totalRows": table.num_rows or 0,
                    "fetchedRows": len(rows),
                    "pageInfo": {
                        "nextPageToken": page.next_page_token,
                        "hasNextPage": page.next_page_token is not None,
                    },
                    "metadata": {
                        "cost": 0.0,  # tabledata.list is FREE
                        "apiUsed": "tabledata.list",
                    },
                }

                logger.info(
                    "✅ preview_fetched",
                    dataset=dataset_id,
                    table=table_name,
                    fetched_rows=len(rows),
                    total_rows=table.num_rows or 0,
                    has_next_page=page.next_page_token is not None,
                    cost=0.0,
                )

                return result

            except Exception as e:
                error_str = str(e)

                # Check for specific error types
                if "Not found" in error_str or "404" in error_str:
                    logger.error(
                        "table_not_found",
                        dataset=dataset_id,
                        table=table_name,
                        error=error_str,
                    )
                    raise ValueError(f"Table {dataset_id}.{table_name} not found")
                elif "Invalid page token" in error_str or "pageToken" in error_str:
                    logger.error(
                        "invalid_page_token",
                        dataset=dataset_id,
                        table=table_name,
                        page_token=page_token[:20] + "..." if page_token and len(page_token) > 20 else page_token,
                        error=error_str,
                    )
                    raise ValueError(f"Invalid page token: {error_str}")
                else:
                    logger.error(
                        "preview_table_failed",
                        dataset=dataset_id,
                        table=table_name,
                        error=error_str,
                    )
                    raise

        # Run sync operation in thread pool to avoid blocking event loop
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _sync_preview)

    @staticmethod
    def hash_query(sql: str) -> str:
        """
        Generate SHA256 hash of SQL query (for cache keys and logging).

        Args:
            sql: SQL query string

        Returns:
            Hex hash string
        """
        # Normalize: strip whitespace, convert to lowercase
        normalized = " ".join(sql.split()).lower()
        return hashlib.sha256(normalized.encode()).hexdigest()


# Singleton instance
_bigquery_client: Optional[BigQueryClient] = None


def get_bigquery_client() -> BigQueryClient:
    """Get singleton BigQuery client instance."""
    global _bigquery_client
    if _bigquery_client is None:
        _bigquery_client = BigQueryClient()
    return _bigquery_client
