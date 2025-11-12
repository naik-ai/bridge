"""
Connection service for managing database connections with encrypted credentials.
Handles credential encryption/decryption using Cloud KMS and storage in GCS.
"""

import json
import logging
from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID

from google.cloud import kms, storage
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.config import settings
from ..models.db_models import Connection, ConnectionStatus, ConnectionType, Team

logger = logging.getLogger(__name__)


class ConnectionService:
    """Service for managing database connections and encrypted credentials."""

    def __init__(self, db: AsyncSession):
        """Initialize connection service.

        Args:
            db: Database session

        Raises:
            ValueError: If GCS/KMS not configured
        """
        if not settings.gcs_credentials_bucket:
            raise ValueError("GCS credentials bucket not configured")
        if not settings.kms_key_ring or not settings.kms_crypto_key:
            raise ValueError("Cloud KMS not configured")

        self.db = db
        self.kms_client = kms.KeyManagementServiceClient()
        self.gcs_client = storage.Client()
        self.credentials_bucket = self.gcs_client.bucket(settings.gcs_credentials_bucket)

        # Construct KMS key name
        self.kms_key_name = self.kms_client.crypto_key_path(
            settings.gcp_project_id,
            settings.kms_location,
            settings.kms_key_ring,
            settings.kms_crypto_key
        )

    async def create_connection(
        self,
        team_id: UUID,
        name: str,
        connection_type: ConnectionType,
        credentials: Dict[str, Any],
    ) -> Connection:
        """Create a new connection with encrypted credentials.

        Args:
            team_id: Team ID
            name: Connection name
            connection_type: Type of database connection
            credentials: Unencrypted credentials dict

        Returns:
            Created connection

        Raises:
            ValueError: If team not found
        """
        # Verify team exists
        team = await self.db.get(Team, team_id)
        if not team:
            raise ValueError(f"Team {team_id} not found")

        # Encrypt and store credentials
        credentials_path = await self._store_encrypted_credentials(
            team_id, name, credentials
        )

        # Create connection record
        connection = Connection(
            team_id=team_id,
            name=name,
            connection_type=connection_type,
            credentials_path=credentials_path,
            status=ConnectionStatus.testing,
        )

        self.db.add(connection)
        await self.db.commit()
        await self.db.refresh(connection)

        logger.info(f"Created connection {connection.id} for team {team_id}")
        return connection

    async def get_connection(self, connection_id: UUID) -> Optional[Connection]:
        """Get connection by ID.

        Args:
            connection_id: Connection ID

        Returns:
            Connection or None
        """
        return await self.db.get(Connection, connection_id)

    async def list_connections(self, team_id: UUID) -> list[Connection]:
        """List all connections for a team.

        Args:
            team_id: Team ID

        Returns:
            List of connections
        """
        result = await self.db.execute(
            select(Connection).where(Connection.team_id == team_id)
        )
        return list(result.scalars().all())

    async def get_decrypted_credentials(self, connection_id: UUID) -> Dict[str, Any]:
        """Get decrypted credentials for a connection.

        Args:
            connection_id: Connection ID

        Returns:
            Decrypted credentials dict

        Raises:
            ValueError: If connection not found
        """
        connection = await self.get_connection(connection_id)
        if not connection:
            raise ValueError(f"Connection {connection_id} not found")

        return await self._load_encrypted_credentials(connection.credentials_path)

    async def update_connection_status(
        self,
        connection_id: UUID,
        status: ConnectionStatus,
    ) -> Connection:
        """Update connection status.

        Args:
            connection_id: Connection ID
            status: New status

        Returns:
            Updated connection

        Raises:
            ValueError: If connection not found
        """
        connection = await self.get_connection(connection_id)
        if not connection:
            raise ValueError(f"Connection {connection_id} not found")

        connection.status = status
        connection.last_tested_at = datetime.utcnow()
        connection.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(connection)

        logger.info(f"Updated connection {connection_id} status to {status}")
        return connection

    async def test_connection(self, connection_id: UUID) -> bool:
        """Test a database connection.

        Args:
            connection_id: Connection ID

        Returns:
            True if connection successful
        """
        connection = await self.get_connection(connection_id)
        if not connection:
            raise ValueError(f"Connection {connection_id} not found")

        try:
            credentials = await self.get_decrypted_credentials(connection_id)

            # Test connection based on type
            if connection.connection_type == ConnectionType.bigquery:
                success = await self._test_bigquery_connection(credentials)
            elif connection.connection_type == ConnectionType.postgres:
                success = await self._test_postgres_connection(credentials)
            elif connection.connection_type == ConnectionType.snowflake:
                success = await self._test_snowflake_connection(credentials)
            else:
                raise ValueError(f"Unsupported connection type: {connection.connection_type}")

            # Update status
            new_status = ConnectionStatus.active if success else ConnectionStatus.failed
            await self.update_connection_status(connection_id, new_status)

            return success
        except Exception as e:
            logger.error(f"Connection test failed for {connection_id}: {e}")
            await self.update_connection_status(connection_id, ConnectionStatus.failed)
            return False

    async def delete_connection(self, connection_id: UUID) -> None:
        """Delete a connection and its encrypted credentials.

        Args:
            connection_id: Connection ID

        Raises:
            ValueError: If connection not found
        """
        connection = await self.get_connection(connection_id)
        if not connection:
            raise ValueError(f"Connection {connection_id} not found")

        # Delete encrypted credentials from GCS
        try:
            blob = self.credentials_bucket.blob(connection.credentials_path)
            blob.delete()
            logger.info(f"Deleted credentials for connection {connection_id}")
        except Exception as e:
            logger.error(f"Failed to delete credentials: {e}")

        # Delete connection record
        await self.db.delete(connection)
        await self.db.commit()

        logger.info(f"Deleted connection {connection_id}")

    # Private methods for credential encryption/decryption

    async def _store_encrypted_credentials(
        self,
        team_id: UUID,
        connection_name: str,
        credentials: Dict[str, Any],
    ) -> str:
        """Encrypt and store credentials in GCS.

        Args:
            team_id: Team ID
            connection_name: Connection name
            credentials: Unencrypted credentials

        Returns:
            GCS path to encrypted credentials
        """
        # Serialize credentials
        credentials_json = json.dumps(credentials).encode("utf-8")

        # Encrypt with Cloud KMS
        encrypt_response = self.kms_client.encrypt(
            request={"name": self.kms_key_name, "plaintext": credentials_json}
        )
        encrypted_data = encrypt_response.ciphertext

        # Store in GCS
        blob_path = f"{settings.gcs_credentials_prefix}{team_id}/{connection_name}.enc"
        blob = self.credentials_bucket.blob(blob_path)
        blob.upload_from_string(encrypted_data)

        logger.info(f"Stored encrypted credentials at {blob_path}")
        return blob_path

    async def _load_encrypted_credentials(self, credentials_path: str) -> Dict[str, Any]:
        """Load and decrypt credentials from GCS.

        Args:
            credentials_path: GCS path to encrypted credentials

        Returns:
            Decrypted credentials dict
        """
        # Load from GCS
        blob = self.credentials_bucket.blob(credentials_path)
        encrypted_data = blob.download_as_bytes()

        # Decrypt with Cloud KMS
        decrypt_response = self.kms_client.decrypt(
            request={"name": self.kms_key_name, "ciphertext": encrypted_data}
        )
        decrypted_data = decrypt_response.plaintext

        # Deserialize
        credentials = json.loads(decrypted_data.decode("utf-8"))
        return credentials

    # Private methods for testing connections

    async def _test_bigquery_connection(self, credentials: Dict[str, Any]) -> bool:
        """Test BigQuery connection.

        Args:
            credentials: BigQuery credentials

        Returns:
            True if connection successful
        """
        from google.cloud import bigquery
        from google.oauth2 import service_account

        try:
            # Create credentials from dict
            creds = service_account.Credentials.from_service_account_info(credentials)
            client = bigquery.Client(credentials=creds, project=credentials.get("project_id"))

            # Simple query to test connection
            query = "SELECT 1 as test"
            client.query(query).result()

            return True
        except Exception as e:
            logger.error(f"BigQuery connection test failed: {e}")
            return False

    async def _test_postgres_connection(self, credentials: Dict[str, Any]) -> bool:
        """Test Postgres connection.

        Args:
            credentials: Postgres credentials (host, port, database, user, password)

        Returns:
            True if connection successful
        """
        import asyncpg

        try:
            conn = await asyncpg.connect(
                host=credentials["host"],
                port=credentials.get("port", 5432),
                database=credentials["database"],
                user=credentials["user"],
                password=credentials["password"],
            )
            await conn.close()
            return True
        except Exception as e:
            logger.error(f"Postgres connection test failed: {e}")
            return False

    async def _test_snowflake_connection(self, credentials: Dict[str, Any]) -> bool:
        """Test Snowflake connection.

        Args:
            credentials: Snowflake credentials (account, user, password, warehouse, database)

        Returns:
            True if connection successful
        """
        try:
            import snowflake.connector

            conn = snowflake.connector.connect(
                account=credentials["account"],
                user=credentials["user"],
                password=credentials["password"],
                warehouse=credentials.get("warehouse"),
                database=credentials.get("database"),
            )
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Snowflake connection test failed: {e}")
            return False


# Dependency injection
async def get_connection_service(db: AsyncSession) -> ConnectionService:
    """Get connection service instance."""
    return ConnectionService(db)
