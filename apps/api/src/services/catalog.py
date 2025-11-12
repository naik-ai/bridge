"""
Catalog service for discovering and scanning database schemas.
Supports BigQuery, Postgres, and Snowflake schema introspection.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.db_models import (
    CatalogJobStatus,
    Connection,
    ConnectionType,
    Dataset,
    Table,
)
from .connection import ConnectionService

logger = logging.getLogger(__name__)


class CatalogService:
    """Service for discovering and scanning database schemas."""

    def __init__(self, db: AsyncSession, connection_service: ConnectionService):
        """Initialize catalog service.

        Args:
            db: Database session
            connection_service: Connection service for credential access
        """
        self.db = db
        self.connection_service = connection_service

    async def discover_datasets(self, connection_id: UUID) -> List[Dataset]:
        """Discover all datasets/schemas from a connection.

        Args:
            connection_id: Connection ID

        Returns:
            List of discovered datasets
        """
        connection = await self.connection_service.get_connection(connection_id)
        if not connection:
            raise ValueError(f"Connection {connection_id} not found")

        credentials = await self.connection_service.get_decrypted_credentials(connection_id)

        # Discover based on connection type
        if connection.connection_type == ConnectionType.bigquery:
            dataset_info = await self._discover_bigquery_datasets(credentials)
        elif connection.connection_type == ConnectionType.postgres:
            dataset_info = await self._discover_postgres_schemas(credentials)
        elif connection.connection_type == ConnectionType.snowflake:
            dataset_info = await self._discover_snowflake_schemas(credentials)
        else:
            raise ValueError(f"Unsupported connection type: {connection.connection_type}")

        # Create or update dataset records
        datasets = []
        for info in dataset_info:
            # Check if dataset exists
            result = await self.db.execute(
                select(Dataset).where(
                    Dataset.connection_id == connection_id,
                    Dataset.fully_qualified_name == info["fully_qualified_name"],
                )
            )
            existing = result.scalar_one_or_none()

            if existing:
                # Update existing
                existing.description = info.get("description")
                existing.last_scanned_at = datetime.utcnow()
                dataset = existing
            else:
                # Create new
                dataset = Dataset(
                    connection_id=connection_id,
                    name=info["name"],
                    fully_qualified_name=info["fully_qualified_name"],
                    description=info.get("description"),
                    catalog_job_status=CatalogJobStatus.pending,
                )
                self.db.add(dataset)

            datasets.append(dataset)

        await self.db.commit()
        logger.info(f"Discovered {len(datasets)} datasets for connection {connection_id}")
        return datasets

    async def scan_dataset_tables(self, dataset_id: UUID) -> List[Table]:
        """Scan all tables in a dataset.

        Args:
            dataset_id: Dataset ID

        Returns:
            List of discovered tables
        """
        dataset = await self.db.get(Dataset, dataset_id)
        if not dataset:
            raise ValueError(f"Dataset {dataset_id} not found")

        # Update dataset status
        dataset.catalog_job_status = CatalogJobStatus.running
        await self.db.commit()

        try:
            connection = await self.connection_service.get_connection(dataset.connection_id)
            credentials = await self.connection_service.get_decrypted_credentials(
                dataset.connection_id
            )

            # Scan based on connection type
            if connection.connection_type == ConnectionType.bigquery:
                table_info = await self._scan_bigquery_tables(credentials, dataset.name)
            elif connection.connection_type == ConnectionType.postgres:
                table_info = await self._scan_postgres_tables(credentials, dataset.name)
            elif connection.connection_type == ConnectionType.snowflake:
                table_info = await self._scan_snowflake_tables(credentials, dataset.name)
            else:
                raise ValueError(f"Unsupported connection type: {connection.connection_type}")

            # Create or update table records
            tables = []
            for info in table_info:
                # Check if table exists
                result = await self.db.execute(
                    select(Table).where(
                        Table.dataset_id == dataset_id,
                        Table.fully_qualified_name == info["fully_qualified_name"],
                    )
                )
                existing = result.scalar_one_or_none()

                if existing:
                    # Update existing
                    existing.description = info.get("description")
                    existing.schema = info.get("schema")
                    existing.row_count = info.get("row_count")
                    existing.size_bytes = info.get("size_bytes")
                    existing.last_scanned_at = datetime.utcnow()
                    table = existing
                else:
                    # Create new
                    table = Table(
                        dataset_id=dataset_id,
                        name=info["name"],
                        fully_qualified_name=info["fully_qualified_name"],
                        description=info.get("description"),
                        schema=info.get("schema"),
                        row_count=info.get("row_count"),
                        size_bytes=info.get("size_bytes"),
                    )
                    self.db.add(table)

                tables.append(table)

            # Update dataset status
            dataset.catalog_job_status = CatalogJobStatus.completed
            dataset.last_scanned_at = datetime.utcnow()

            await self.db.commit()
            logger.info(f"Scanned {len(tables)} tables in dataset {dataset_id}")
            return tables

        except Exception as e:
            logger.error(f"Failed to scan dataset {dataset_id}: {e}")
            dataset.catalog_job_status = CatalogJobStatus.failed
            await self.db.commit()
            raise

    async def get_dataset_tables(self, dataset_id: UUID) -> List[Table]:
        """Get all tables for a dataset.

        Args:
            dataset_id: Dataset ID

        Returns:
            List of tables
        """
        result = await self.db.execute(
            select(Table).where(Table.dataset_id == dataset_id)
        )
        return list(result.scalars().all())

    async def get_table_schema(self, table_id: UUID) -> Optional[List[Dict[str, Any]]]:
        """Get table schema.

        Args:
            table_id: Table ID

        Returns:
            Table schema or None
        """
        table = await self.db.get(Table, table_id)
        return table.schema if table else None

    # Private methods for BigQuery discovery

    async def _discover_bigquery_datasets(
        self, credentials: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Discover BigQuery datasets.

        Args:
            credentials: BigQuery credentials

        Returns:
            List of dataset info dicts
        """
        from google.cloud import bigquery
        from google.oauth2 import service_account

        creds = service_account.Credentials.from_service_account_info(credentials)
        client = bigquery.Client(credentials=creds, project=credentials.get("project_id"))

        datasets = []
        for dataset in client.list_datasets():
            dataset_ref = client.get_dataset(dataset.reference)
            datasets.append({
                "name": dataset.dataset_id,
                "fully_qualified_name": f"{dataset.project}.{dataset.dataset_id}",
                "description": dataset_ref.description,
            })

        return datasets

    async def _scan_bigquery_tables(
        self, credentials: Dict[str, Any], dataset_name: str
    ) -> List[Dict[str, Any]]:
        """Scan BigQuery tables in a dataset.

        Args:
            credentials: BigQuery credentials
            dataset_name: Dataset name

        Returns:
            List of table info dicts
        """
        from google.cloud import bigquery
        from google.oauth2 import service_account

        creds = service_account.Credentials.from_service_account_info(credentials)
        client = bigquery.Client(credentials=creds, project=credentials.get("project_id"))

        tables = []
        dataset_ref = client.dataset(dataset_name)

        for table_item in client.list_tables(dataset_ref):
            table_ref = dataset_ref.table(table_item.table_id)
            table = client.get_table(table_ref)

            # Extract schema
            schema = [
                {
                    "name": field.name,
                    "type": field.field_type,
                    "mode": field.mode,
                    "description": field.description,
                }
                for field in table.schema
            ]

            tables.append({
                "name": table.table_id,
                "fully_qualified_name": f"{table.project}.{table.dataset_id}.{table.table_id}",
                "description": table.description,
                "schema": schema,
                "row_count": table.num_rows,
                "size_bytes": table.num_bytes,
            })

        return tables

    # Private methods for Postgres discovery

    async def _discover_postgres_schemas(
        self, credentials: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Discover Postgres schemas.

        Args:
            credentials: Postgres credentials

        Returns:
            List of schema info dicts
        """
        import asyncpg

        conn = await asyncpg.connect(
            host=credentials["host"],
            port=credentials.get("port", 5432),
            database=credentials["database"],
            user=credentials["user"],
            password=credentials["password"],
        )

        query = """
        SELECT schema_name
        FROM information_schema.schemata
        WHERE schema_name NOT IN ('pg_catalog', 'information_schema', 'pg_toast')
        ORDER BY schema_name
        """

        rows = await conn.fetch(query)
        await conn.close()

        return [
            {
                "name": row["schema_name"],
                "fully_qualified_name": f"{credentials['database']}.{row['schema_name']}",
            }
            for row in rows
        ]

    async def _scan_postgres_tables(
        self, credentials: Dict[str, Any], schema_name: str
    ) -> List[Dict[str, Any]]:
        """Scan Postgres tables in a schema.

        Args:
            credentials: Postgres credentials
            schema_name: Schema name

        Returns:
            List of table info dicts
        """
        import asyncpg

        conn = await asyncpg.connect(
            host=credentials["host"],
            port=credentials.get("port", 5432),
            database=credentials["database"],
            user=credentials["user"],
            password=credentials["password"],
        )

        # Get tables
        tables_query = """
        SELECT
            table_name,
            obj_description((quote_ident($1) || '.' || quote_ident(table_name))::regclass) as description
        FROM information_schema.tables
        WHERE table_schema = $1
        AND table_type = 'BASE TABLE'
        ORDER BY table_name
        """

        table_rows = await conn.fetch(tables_query, schema_name)

        tables = []
        for table_row in table_rows:
            table_name = table_row["table_name"]

            # Get columns
            columns_query = """
            SELECT
                column_name,
                data_type,
                is_nullable,
                col_description((quote_ident($1) || '.' || quote_ident($2))::regclass, ordinal_position) as description
            FROM information_schema.columns
            WHERE table_schema = $1 AND table_name = $2
            ORDER BY ordinal_position
            """

            column_rows = await conn.fetch(columns_query, schema_name, table_name)

            schema = [
                {
                    "name": col["column_name"],
                    "type": col["data_type"],
                    "nullable": col["is_nullable"] == "YES",
                    "description": col["description"],
                }
                for col in column_rows
            ]

            # Get row count (approximate)
            count_query = f"""
            SELECT reltuples::bigint as row_count, relpages * 8192 as size_bytes
            FROM pg_class
            WHERE oid = (quote_ident($1) || '.' || quote_ident($2))::regclass
            """
            count_row = await conn.fetchrow(count_query, schema_name, table_name)

            tables.append({
                "name": table_name,
                "fully_qualified_name": f"{credentials['database']}.{schema_name}.{table_name}",
                "description": table_row["description"],
                "schema": schema,
                "row_count": count_row["row_count"] if count_row else None,
                "size_bytes": count_row["size_bytes"] if count_row else None,
            })

        await conn.close()
        return tables

    # Private methods for Snowflake discovery

    async def _discover_snowflake_schemas(
        self, credentials: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Discover Snowflake schemas.

        Args:
            credentials: Snowflake credentials

        Returns:
            List of schema info dicts
        """
        import snowflake.connector

        conn = snowflake.connector.connect(
            account=credentials["account"],
            user=credentials["user"],
            password=credentials["password"],
            warehouse=credentials.get("warehouse"),
            database=credentials.get("database"),
        )

        cursor = conn.cursor()
        cursor.execute("SHOW SCHEMAS")

        schemas = []
        for row in cursor:
            schema_name = row[1]  # Schema name is in second column
            if schema_name not in ("INFORMATION_SCHEMA", "PUBLIC"):
                schemas.append({
                    "name": schema_name,
                    "fully_qualified_name": f"{credentials['database']}.{schema_name}",
                })

        cursor.close()
        conn.close()
        return schemas

    async def _scan_snowflake_tables(
        self, credentials: Dict[str, Any], schema_name: str
    ) -> List[Dict[str, Any]]:
        """Scan Snowflake tables in a schema.

        Args:
            credentials: Snowflake credentials
            schema_name: Schema name

        Returns:
            List of table info dicts
        """
        import snowflake.connector

        conn = snowflake.connector.connect(
            account=credentials["account"],
            user=credentials["user"],
            password=credentials["password"],
            warehouse=credentials.get("warehouse"),
            database=credentials.get("database"),
        )

        cursor = conn.cursor()

        # Get tables
        cursor.execute(f"SHOW TABLES IN SCHEMA {schema_name}")
        table_rows = cursor.fetchall()

        tables = []
        for table_row in table_rows:
            table_name = table_row[1]  # Table name is in second column

            # Get columns
            cursor.execute(f"DESCRIBE TABLE {schema_name}.{table_name}")
            column_rows = cursor.fetchall()

            schema = [
                {
                    "name": col[0],  # Column name
                    "type": col[1],  # Data type
                    "nullable": col[3] == "Y",  # Nullable
                    "description": col[8] if len(col) > 8 else None,  # Comment
                }
                for col in column_rows
            ]

            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {schema_name}.{table_name}")
            row_count = cursor.fetchone()[0]

            tables.append({
                "name": table_name,
                "fully_qualified_name": f"{credentials['database']}.{schema_name}.{table_name}",
                "description": table_row[7] if len(table_row) > 7 else None,  # Comment
                "schema": schema,
                "row_count": row_count,
                "size_bytes": None,  # Snowflake doesn't easily expose size
            })

        cursor.close()
        conn.close()
        return tables


# Dependency injection
async def get_catalog_service(
    db: AsyncSession, connection_service: ConnectionService
) -> CatalogService:
    """Get catalog service instance."""
    return CatalogService(db, connection_service)
