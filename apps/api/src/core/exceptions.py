"""
Custom exceptions for Peter Dashboard Platform.
Provides domain-specific exceptions with structured error information.

PDR Reference: §10 (Risks & Mitigations), §11 (Acceptance Criteria)
"""

from typing import Any, Optional


class PeterException(Exception):
    """Base exception for all Peter platform errors."""

    def __init__(
        self,
        message: str,
        error_code: str,
        details: Optional[dict[str, Any]] = None,
        original_error: Optional[Exception] = None,
    ):
        """
        Initialize base exception.

        Args:
            message: Human-readable error message
            error_code: Machine-readable error code
            details: Additional error context
            original_error: Original exception if wrapping another error
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        self.original_error = original_error


# Validation Exceptions (400)
class ValidationException(PeterException):
    """Raised when validation fails."""

    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        reason: Optional[str] = None,
        details: Optional[dict[str, Any]] = None,
    ):
        """Initialize validation exception."""
        error_details = details or {}
        if field:
            error_details["field"] = field
        if reason:
            error_details["reason"] = reason

        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            details=error_details,
        )


class YAMLValidationException(ValidationException):
    """Raised when YAML validation fails (PDR §4, §8)."""

    def __init__(self, message: str, errors: list[dict[str, Any]] | None = None):
        """Initialize YAML validation exception."""
        super().__init__(
            message=message,
            details={"validation_errors": errors} if errors else {},
        )


class SQLValidationException(ValidationException):
    """Raised when SQL validation fails (PDR §4)."""

    def __init__(
        self,
        message: str,
        sql_preview: Optional[str] = None,
        query_hash: Optional[str] = None,
    ):
        """Initialize SQL validation exception."""
        details = {}
        if sql_preview:
            details["sql_preview"] = sql_preview[:200]
        if query_hash:
            details["query_hash"] = query_hash

        super().__init__(
            message=message,
            details=details,
        )


class GridPositionException(ValidationException):
    """Raised when grid layout validation fails (PDR §8)."""

    def __init__(self, message: str, chart_id: Optional[str] = None):
        """Initialize grid position exception."""
        super().__init__(
            message=message,
            field="layout.position",
            details={"chart_id": chart_id} if chart_id else {},
        )


class QueryReferenceException(ValidationException):
    """Raised when query reference is missing (PDR §8)."""

    def __init__(self, query_ref: str, chart_id: Optional[str] = None):
        """Initialize query reference exception."""
        super().__init__(
            message=f"Query reference '{query_ref}' not found in dashboard queries",
            field="query_ref",
            details={"query_ref": query_ref, "chart_id": chart_id} if chart_id else {"query_ref": query_ref},
        )


# Authentication Exceptions (401)
class AuthenticationException(PeterException):
    """Raised when authentication fails (PDR §6)."""

    def __init__(self, message: str = "Authentication required"):
        """Initialize authentication exception."""
        super().__init__(
            message=message,
            error_code="AUTHENTICATION_REQUIRED",
        )


class InvalidTokenException(AuthenticationException):
    """Raised when session token is invalid."""

    def __init__(self, message: str = "Invalid or expired session token"):
        """Initialize invalid token exception."""
        super().__init__(message)
        self.error_code = "INVALID_TOKEN"


class SessionExpiredException(AuthenticationException):
    """Raised when session has expired."""

    def __init__(self, expires_at: Optional[str] = None):
        """Initialize session expired exception."""
        details = {"expires_at": expires_at} if expires_at else {}
        super().__init__(message="Session has expired")
        self.error_code = "SESSION_EXPIRED"
        self.details = details


# Authorization Exceptions (403)
class AuthorizationException(PeterException):
    """Raised when authorization fails (PDR §6)."""

    def __init__(
        self,
        message: str = "Access forbidden",
        required_permission: Optional[str] = None,
    ):
        """Initialize authorization exception."""
        details = {"required_permission": required_permission} if required_permission else {}
        super().__init__(
            message=message,
            error_code="INSUFFICIENT_PERMISSIONS",
            details=details,
        )


class EmailNotAllowedException(AuthorizationException):
    """Raised when email is not in allowlist (PDR §6)."""

    def __init__(self, email: str):
        """Initialize email not allowed exception."""
        super().__init__(
            message=f"Email '{email}' is not in the allowlist",
            required_permission="email_allowlist",
        )
        self.error_code = "EMAIL_NOT_ALLOWED"
        self.details["email"] = email


# Resource Not Found Exceptions (404)
class NotFoundException(PeterException):
    """Raised when a resource is not found."""

    def __init__(self, resource_type: str, identifier: str):
        """Initialize not found exception."""
        super().__init__(
            message=f"{resource_type.title()} '{identifier}' not found",
            error_code=f"{resource_type.upper()}_NOT_FOUND",
            details={"resource_type": resource_type, "identifier": identifier},
        )


class DashboardNotFoundException(NotFoundException):
    """Raised when dashboard is not found (PDR §4)."""

    def __init__(self, slug: str):
        """Initialize dashboard not found exception."""
        super().__init__(resource_type="dashboard", identifier=slug)


class QueryNotFoundException(NotFoundException):
    """Raised when query is not found."""

    def __init__(self, query_id: str):
        """Initialize query not found exception."""
        super().__init__(resource_type="query", identifier=query_id)


class UserNotFoundException(NotFoundException):
    """Raised when user is not found."""

    def __init__(self, identifier: str):
        """Initialize user not found exception."""
        super().__init__(resource_type="user", identifier=identifier)


# BigQuery Exceptions (422)
class BigQueryException(PeterException):
    """Raised when BigQuery operation fails (PDR §9)."""

    def __init__(
        self,
        message: str,
        query_hash: Optional[str] = None,
        bytes_scanned: Optional[int] = None,
        job_id: Optional[str] = None,
        original_error: Optional[Exception] = None,
    ):
        """Initialize BigQuery exception."""
        details = {}
        if query_hash:
            details["query_hash"] = query_hash
        if bytes_scanned is not None:
            details["bytes_scanned"] = bytes_scanned
        if job_id:
            details["job_id"] = job_id

        super().__init__(
            message=message,
            error_code="BIGQUERY_ERROR",
            details=details,
            original_error=original_error,
        )


class BytesLimitExceededException(BigQueryException):
    """Raised when query exceeds maximum_bytes_billed cap (PDR §9)."""

    def __init__(
        self,
        bytes_attempted: int,
        max_bytes_allowed: int,
        query_hash: Optional[str] = None,
    ):
        """Initialize bytes limit exceeded exception."""
        message = (
            f"Query would scan {bytes_attempted:,} bytes, exceeding limit of {max_bytes_allowed:,} bytes "
            f"({max_bytes_allowed / (1024**2):.0f}MB)"
        )
        super().__init__(
            message=message,
            query_hash=query_hash,
            bytes_scanned=bytes_attempted,
        )
        self.error_code = "BYTES_LIMIT_EXCEEDED"
        self.details["max_bytes_allowed"] = max_bytes_allowed


class QueryTimeoutException(BigQueryException):
    """Raised when query execution times out (PDR §9)."""

    def __init__(
        self,
        timeout_seconds: int,
        query_hash: Optional[str] = None,
        job_id: Optional[str] = None,
    ):
        """Initialize query timeout exception."""
        message = f"Query execution exceeded timeout of {timeout_seconds} seconds"
        super().__init__(
            message=message,
            query_hash=query_hash,
            job_id=job_id,
        )
        self.error_code = "QUERY_TIMEOUT"
        self.details["timeout_seconds"] = timeout_seconds


class DangerousSQLException(BigQueryException):
    """Raised when SQL contains dangerous patterns (PDR §10)."""

    def __init__(self, pattern: str, sql_preview: Optional[str] = None):
        """Initialize dangerous SQL exception."""
        message = f"SQL contains dangerous pattern: {pattern}"
        super().__init__(
            message=message,
        )
        self.error_code = "QUERY_VALIDATION_FAILED"
        if sql_preview:
            self.details["sql_preview"] = sql_preview[:200]
        self.details["dangerous_pattern"] = pattern


# Storage Exceptions (500)
class StorageException(PeterException):
    """Raised when storage operation fails (PDR §3)."""

    def __init__(
        self,
        message: str,
        storage_path: Optional[str] = None,
        operation: Optional[str] = None,
        original_error: Optional[Exception] = None,
    ):
        """Initialize storage exception."""
        details = {}
        if storage_path:
            details["storage_path"] = storage_path
        if operation:
            details["operation"] = operation

        super().__init__(
            message=message,
            error_code="STORAGE_ERROR",
            details=details,
            original_error=original_error,
        )


class DashboardAlreadyExistsException(StorageException):
    """Raised when attempting to create a dashboard that already exists."""

    def __init__(self, slug: str):
        """Initialize dashboard already exists exception."""
        super().__init__(
            message=f"Dashboard with slug '{slug}' already exists",
            storage_path=slug,
            operation="create",
        )
        self.error_code = "DASHBOARD_ALREADY_EXISTS"


# Database Exceptions (500)
class DatabaseException(PeterException):
    """Raised when database operation fails."""

    def __init__(
        self,
        message: str,
        operation: Optional[str] = None,
        original_error: Optional[Exception] = None,
    ):
        """Initialize database exception."""
        details = {}
        if operation:
            details["operation"] = operation

        super().__init__(
            message=message,
            error_code="DATABASE_ERROR",
            details=details,
            original_error=original_error,
        )


# Cache Exceptions (503)
class CacheException(PeterException):
    """Raised when cache operation fails (PDR §5)."""

    def __init__(
        self,
        message: str,
        cache_key: Optional[str] = None,
        operation: Optional[str] = None,
        original_error: Optional[Exception] = None,
    ):
        """Initialize cache exception."""
        details = {}
        if cache_key:
            details["cache_key"] = cache_key
        if operation:
            details["operation"] = operation

        super().__init__(
            message=message,
            error_code="CACHE_UNAVAILABLE",
            details=details,
            original_error=original_error,
        )


# Compilation Exceptions
class CompilationException(PeterException):
    """Raised when dashboard compilation fails (PDR §4)."""

    def __init__(
        self,
        message: str,
        dashboard_slug: Optional[str] = None,
        compilation_stage: Optional[str] = None,
    ):
        """Initialize compilation exception."""
        details = {}
        if dashboard_slug:
            details["dashboard_slug"] = dashboard_slug
        if compilation_stage:
            details["compilation_stage"] = compilation_stage

        super().__init__(
            message=message,
            error_code="COMPILATION_ERROR",
            details=details,
        )


# Lineage Exceptions
class LineageException(PeterException):
    """Raised when lineage operation fails (PDR §7)."""

    def __init__(
        self,
        message: str,
        dashboard_slug: Optional[str] = None,
        node_id: Optional[str] = None,
    ):
        """Initialize lineage exception."""
        details = {}
        if dashboard_slug:
            details["dashboard_slug"] = dashboard_slug
        if node_id:
            details["node_id"] = node_id

        super().__init__(
            message=message,
            error_code="LINEAGE_ERROR",
            details=details,
        )


# Rate Limiting Exception
class RateLimitException(PeterException):
    """Raised when rate limit is exceeded."""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: Optional[int] = None,
    ):
        """Initialize rate limit exception."""
        details = {}
        if retry_after:
            details["retry_after_seconds"] = retry_after

        super().__init__(
            message=message,
            error_code="RATE_LIMIT_EXCEEDED",
            details=details,
        )
