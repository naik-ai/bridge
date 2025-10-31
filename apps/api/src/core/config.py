"""
Application configuration using Pydantic Settings.
Loads from environment variables with validation.
"""

from functools import lru_cache
from typing import List, Literal

from pydantic import Field, PostgresDsn, RedisDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = Field(default="peter-api", description="Application name")
    app_env: Literal["development", "staging", "production"] = Field(
        default="development", description="Environment"
    )
    app_version: str = Field(default="0.1.0", description="Application version")
    debug: bool = Field(default=False, description="Debug mode")
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO", description="Logging level"
    )

    # API Server
    api_host: str = Field(default="0.0.0.0", description="API host")
    api_port: int = Field(default=8000, description="API port")
    api_workers: int = Field(default=4, description="Number of workers")

    # CORS
    cors_origins: List[str] = Field(
        default_factory=lambda: ["http://localhost:3000"],
        description="Allowed CORS origins",
    )
    cors_allow_credentials: bool = Field(default=True, description="Allow credentials")

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: str | List[str]) -> List[str]:
        """Parse comma-separated CORS origins."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    # Database (Postgres)
    database_url: PostgresDsn = Field(description="PostgreSQL connection URL")
    database_pool_size: int = Field(default=20, description="Connection pool size")
    database_max_overflow: int = Field(default=10, description="Max pool overflow")
    database_pool_timeout: int = Field(default=30, description="Pool timeout seconds")
    database_echo: bool = Field(default=False, description="Echo SQL queries")

    # Redis Cache
    redis_url: RedisDsn | None = Field(default=None, description="Redis connection URL")
    redis_password: str | None = Field(default=None, description="Redis password")
    redis_max_connections: int = Field(default=50, description="Max Redis connections")
    cache_default_ttl: int = Field(default=86400, description="Default cache TTL seconds")
    cache_type: Literal["redis", "in-process"] = Field(
        default="in-process", description="Cache backend type"
    )

    # Google Cloud Project
    gcp_project_id: str = Field(description="GCP project ID")
    gcp_region: str = Field(default="us-central1", description="GCP region")
    gcp_service_account_email: str | None = Field(
        default=None, description="Service account email"
    )

    # BigQuery
    bigquery_dataset: str = Field(description="Default BigQuery dataset")
    bigquery_location: str = Field(default="US", description="BigQuery location")
    bigquery_max_bytes_billed: int = Field(
        default=100_000_000, description="Max bytes billed per query (100MB)"
    )
    bigquery_query_timeout: int = Field(default=60, description="Query timeout seconds")
    bigquery_use_query_cache: bool = Field(
        default=True, description="Enable BigQuery result cache"
    )
    bigquery_allowed_datasets: List[str] = Field(
        default_factory=list, description="Allowed datasets for queries"
    )
    bigquery_credentials_path: str | None = Field(
        default=None, description="Path to service account JSON"
    )

    @field_validator("bigquery_allowed_datasets", mode="before")
    @classmethod
    def parse_allowed_datasets(cls, v: str | List[str]) -> List[str]:
        """Parse comma-separated dataset names."""
        if isinstance(v, str):
            return [ds.strip() for ds in v.split(",") if ds.strip()]
        return v

    # Google Cloud Storage (YAML Storage)
    gcs_bucket: str = Field(description="GCS bucket for dashboard YAML files")
    gcs_dashboards_prefix: str = Field(
        default="dashboards/", description="Prefix for dashboard files"
    )

    # Secret Manager
    use_secret_manager: bool = Field(
        default=False, description="Use GCP Secret Manager for secrets"
    )
    secret_manager_project_id: str | None = Field(
        default=None, description="Secret Manager project ID"
    )

    # Authentication (Google OAuth)
    google_oauth_client_id: str = Field(description="Google OAuth client ID")
    google_oauth_client_secret: str = Field(description="Google OAuth client secret")
    google_oauth_redirect_uri: str = Field(description="OAuth redirect URI")
    allowed_emails: List[str] = Field(
        default_factory=list, description="Allowed user emails"
    )
    allowed_email_domains: List[str] = Field(
        default_factory=list, description="Allowed email domains"
    )

    @field_validator("allowed_emails", mode="before")
    @classmethod
    def parse_allowed_emails(cls, v: str | List[str]) -> List[str]:
        """Parse comma-separated emails."""
        if isinstance(v, str):
            return [email.strip().lower() for email in v.split(",") if email.strip()]
        return [email.lower() for email in v]

    @field_validator("allowed_email_domains", mode="before")
    @classmethod
    def parse_allowed_domains(cls, v: str | List[str]) -> List[str]:
        """Parse comma-separated domains."""
        if isinstance(v, str):
            return [domain.strip().lower() for domain in v.split(",") if domain.strip()]
        return [domain.lower() for domain in v]

    # Session Management
    session_secret_key: str = Field(description="Secret key for session encryption")
    session_cookie_name: str = Field(default="peter_session", description="Cookie name")
    session_cookie_secure: bool = Field(default=False, description="Secure cookie flag")
    session_cookie_httponly: bool = Field(default=True, description="HTTPOnly cookie flag")
    session_cookie_samesite: Literal["lax", "strict", "none"] = Field(
        default="lax", description="SameSite cookie attribute"
    )
    session_expires_days: int = Field(default=7, description="Session expiration days")
    session_refresh_threshold_days: int = Field(
        default=1, description="Days before expiry to refresh"
    )

    # OpenTelemetry
    otel_service_name: str = Field(default="peter-api", description="Service name for traces")
    otel_exporter_otlp_endpoint: str | None = Field(
        default=None, description="OTLP exporter endpoint"
    )
    otel_traces_exporter: Literal["gcp_trace", "otlp", "console", "none"] = Field(
        default="gcp_trace", description="Traces exporter type"
    )
    otel_metrics_exporter: Literal["gcp_monitoring", "otlp", "console", "none"] = Field(
        default="none", description="Metrics exporter type"
    )
    otel_logs_exporter: Literal["gcp_logging", "otlp", "console", "none"] = Field(
        default="none", description="Logs exporter type"
    )
    otel_trace_sampling_rate: float = Field(
        default=1.0, ge=0.0, le=1.0, description="Trace sampling rate"
    )
    otel_enable_instrumentation: bool = Field(
        default=True, description="Enable auto-instrumentation"
    )

    # Feature Flags
    enable_precompute: bool = Field(default=True, description="Enable precompute endpoint")
    enable_llm_verification: bool = Field(
        default=True, description="Enable LLM verification loop"
    )
    enable_cost_tracking: bool = Field(
        default=True, description="Enable query cost tracking"
    )
    enable_query_logging: bool = Field(default=True, description="Enable query logging")

    # Rate Limiting
    rate_limit_enabled: bool = Field(default=False, description="Enable rate limiting")
    rate_limit_per_minute: int = Field(default=60, description="Requests per minute")
    rate_limit_per_hour: int = Field(default=1000, description="Requests per hour")

    # Performance Tuning
    max_concurrent_queries: int = Field(
        default=10, description="Max concurrent BigQuery queries"
    )
    query_result_cache_size: int = Field(
        default=1000, description="In-process cache max entries"
    )
    lineage_cache_ttl: int = Field(default=3600, description="Lineage cache TTL seconds")

    # Schema browser configuration
    schema_preview_default_limit: int = Field(
        default=50,
        description="Default page size for table preview"
    )
    schema_preview_max_limit: int = Field(
        default=1000,
        description="Maximum page size for table preview"
    )
    schema_cache_ttl_datasets: int = Field(
        default=3600,
        description="Cache TTL for datasets in seconds (1 hour)"
    )
    schema_cache_ttl_tables: int = Field(
        default=900,
        description="Cache TTL for tables in seconds (15 minutes)"
    )
    schema_cache_ttl_schema: int = Field(
        default=900,
        description="Cache TTL for table schemas in seconds (15 minutes)"
    )

    # Development/Testing
    testing: bool = Field(default=False, description="Testing mode")
    test_database_url: PostgresDsn | None = Field(
        default=None, description="Test database URL"
    )
    mock_bigquery: bool = Field(default=False, description="Mock BigQuery for testing")
    skip_auth: bool = Field(default=False, description="Skip authentication for local dev")

    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.app_env == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development."""
        return self.app_env == "development"

    @property
    def database_url_sync(self) -> str:
        """Get synchronous database URL for Alembic."""
        url_str = str(self.database_url)
        return url_str.replace("postgresql+asyncpg://", "postgresql://")


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Convenience export
settings = get_settings()
