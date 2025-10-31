"""
Google Cloud Secret Manager integration for retrieving secrets.
Falls back to environment variables for local development.
"""

import os
from functools import lru_cache
from typing import Any, Dict

import structlog

logger = structlog.get_logger(__name__)


class SecretsManager:
    """Manage secrets from GCP Secret Manager with environment variable fallback."""

    def __init__(self, project_id: str | None = None, use_secret_manager: bool = False):
        """
        Initialize secrets manager.

        Args:
            project_id: GCP project ID for Secret Manager
            use_secret_manager: Whether to use Secret Manager or environment variables
        """
        self.project_id = project_id
        self.use_secret_manager = use_secret_manager
        self._client = None
        self._cache: Dict[str, Any] = {}

        if self.use_secret_manager and not self.project_id:
            raise ValueError("project_id required when use_secret_manager=True")

    @property
    def client(self) -> Any:
        """Lazy-load Secret Manager client."""
        if self._client is None and self.use_secret_manager:
            try:
                from google.cloud import secretmanager

                self._client = secretmanager.SecretManagerServiceClient()
                logger.info("secret_manager_client_initialized", project_id=self.project_id)
            except ImportError:
                logger.error("google_cloud_secretmanager_not_installed")
                raise ImportError(
                    "google-cloud-secret-manager is required for Secret Manager. "
                    "Install with: uv pip install google-cloud-secret-manager"
                )
        return self._client

    def get_secret(self, secret_name: str, version: str = "latest") -> str:
        """
        Get secret value from Secret Manager or environment variable.

        Args:
            secret_name: Name of the secret
            version: Version of the secret (default: "latest")

        Returns:
            Secret value as string

        Raises:
            ValueError: If secret not found
        """
        # Check cache first
        cache_key = f"{secret_name}:{version}"
        if cache_key in self._cache:
            logger.debug("secret_cache_hit", secret=secret_name)
            return self._cache[cache_key]

        # Try Secret Manager if enabled
        if self.use_secret_manager:
            try:
                value = self._get_from_secret_manager(secret_name, version)
                self._cache[cache_key] = value
                logger.info("secret_retrieved_from_secret_manager", secret=secret_name)
                return value
            except Exception as e:
                logger.warning(
                    "secret_manager_fallback_to_env",
                    secret=secret_name,
                    error=str(e),
                )

        # Fallback to environment variable
        value = self._get_from_env(secret_name)
        if value is None:
            raise ValueError(
                f"Secret '{secret_name}' not found in Secret Manager or environment"
            )

        self._cache[cache_key] = value
        logger.info("secret_retrieved_from_env", secret=secret_name)
        return value

    def _get_from_secret_manager(self, secret_name: str, version: str = "latest") -> str:
        """
        Retrieve secret from GCP Secret Manager.

        Args:
            secret_name: Name of the secret
            version: Version of the secret

        Returns:
            Secret value

        Raises:
            Exception: If retrieval fails
        """
        if not self.client:
            raise ValueError("Secret Manager client not initialized")

        name = f"projects/{self.project_id}/secrets/{secret_name}/versions/{version}"

        try:
            response = self.client.access_secret_version(request={"name": name})
            return response.payload.data.decode("UTF-8")
        except Exception as e:
            logger.error(
                "secret_manager_access_failed",
                secret=secret_name,
                version=version,
                error=str(e),
            )
            raise

    def _get_from_env(self, secret_name: str) -> str | None:
        """
        Get secret from environment variable.

        Args:
            secret_name: Name of the secret (converted to uppercase)

        Returns:
            Environment variable value or None
        """
        # Convert to uppercase and replace hyphens with underscores
        env_var_name = secret_name.upper().replace("-", "_")
        return os.getenv(env_var_name)

    def get_secret_dict(self, secret_name: str, version: str = "latest") -> Dict[str, Any]:
        """
        Get secret and parse as JSON dictionary.

        Args:
            secret_name: Name of the secret
            version: Version of the secret

        Returns:
            Parsed JSON dictionary

        Raises:
            ValueError: If secret is not valid JSON
        """
        import json

        secret_value = self.get_secret(secret_name, version)
        try:
            return json.loads(secret_value)
        except json.JSONDecodeError as e:
            logger.error("secret_json_parse_failed", secret=secret_name, error=str(e))
            raise ValueError(f"Secret '{secret_name}' is not valid JSON") from e

    def clear_cache(self) -> None:
        """Clear the secrets cache."""
        self._cache.clear()
        logger.info("secrets_cache_cleared")


@lru_cache()
def get_secrets_manager() -> SecretsManager:
    """Get cached SecretsManager instance."""
    from src.core.config import settings

    return SecretsManager(
        project_id=settings.secret_manager_project_id or settings.gcp_project_id,
        use_secret_manager=settings.use_secret_manager,
    )


# Convenience function for common secrets
def get_database_credentials() -> Dict[str, str]:
    """
    Get database credentials from Secret Manager.

    Returns:
        Dict with keys: host, port, database, username, password

    Note:
        For local dev, this falls back to DATABASE_URL env var.
        For production, expects 'database-credentials' secret as JSON.
    """
    manager = get_secrets_manager()

    if manager.use_secret_manager:
        try:
            return manager.get_secret_dict("database-credentials")
        except Exception:
            logger.warning("database_credentials_fallback_to_env")

    # Parse from DATABASE_URL environment variable
    from src.core.config import settings

    url = str(settings.database_url)
    # Simple parsing - in production use Secret Manager
    return {"url": url}


def get_oauth_credentials() -> Dict[str, str]:
    """
    Get OAuth credentials from Secret Manager.

    Returns:
        Dict with keys: client_id, client_secret

    Note:
        For local dev, uses environment variables.
        For production, expects 'oauth-credentials' secret as JSON.
    """
    manager = get_secrets_manager()

    if manager.use_secret_manager:
        try:
            return manager.get_secret_dict("oauth-credentials")
        except Exception:
            logger.warning("oauth_credentials_fallback_to_env")

    # Fallback to settings
    from src.core.config import settings

    return {
        "client_id": settings.google_oauth_client_id,
        "client_secret": settings.google_oauth_client_secret,
    }


def get_session_secret() -> str:
    """
    Get session secret key from Secret Manager.

    Returns:
        Session secret key string

    Note:
        For local dev, uses SESSION_SECRET_KEY env var.
        For production, expects 'session-secret-key' secret.
    """
    manager = get_secrets_manager()

    if manager.use_secret_manager:
        try:
            return manager.get_secret("session-secret-key")
        except Exception:
            logger.warning("session_secret_fallback_to_env")

    # Fallback to settings
    from src.core.config import settings

    return settings.session_secret_key


def get_bigquery_credentials() -> str | None:
    """
    Get BigQuery service account credentials path or JSON.

    Returns:
        Path to credentials file or JSON string

    Note:
        For local dev, uses BIGQUERY_CREDENTIALS_PATH or application default.
        For production, expects 'bigquery-service-account' secret as JSON.
    """
    manager = get_secrets_manager()

    if manager.use_secret_manager:
        try:
            # Return JSON string from Secret Manager
            return manager.get_secret("bigquery-service-account")
        except Exception:
            logger.warning("bigquery_credentials_fallback_to_env")

    # Fallback to settings (path to file)
    from src.core.config import settings

    return settings.bigquery_credentials_path
