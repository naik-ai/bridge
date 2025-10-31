"""Response Factory for Peter Dashboard API

Provides standardized response formatting following fee-admin-standalone patterns.
All API responses use consistent envelope with success/error/metadata structure.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Generic, TypeVar
from uuid import uuid4

from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

T = TypeVar("T")


class ErrorCode(str, Enum):
    """Standardized error codes for API responses."""

    # Validation Errors (400)
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INVALID_YAML = "INVALID_YAML"
    INVALID_SQL = "INVALID_SQL"
    INVALID_GRID_POSITION = "INVALID_GRID_POSITION"
    MISSING_QUERY_REF = "MISSING_QUERY_REF"

    # Authentication Errors (401)
    AUTHENTICATION_REQUIRED = "AUTHENTICATION_REQUIRED"
    INVALID_TOKEN = "INVALID_TOKEN"
    SESSION_EXPIRED = "SESSION_EXPIRED"

    # Authorization Errors (403)
    EMAIL_NOT_ALLOWED = "EMAIL_NOT_ALLOWED"
    INSUFFICIENT_PERMISSIONS = "INSUFFICIENT_PERMISSIONS"

    # Resource Errors (404)
    DASHBOARD_NOT_FOUND = "DASHBOARD_NOT_FOUND"
    QUERY_NOT_FOUND = "QUERY_NOT_FOUND"
    USER_NOT_FOUND = "USER_NOT_FOUND"

    # BigQuery Errors (422)
    QUERY_VALIDATION_FAILED = "QUERY_VALIDATION_FAILED"
    BYTES_LIMIT_EXCEEDED = "BYTES_LIMIT_EXCEEDED"
    QUERY_TIMEOUT = "QUERY_TIMEOUT"

    # Cache Errors (503)
    CACHE_UNAVAILABLE = "CACHE_UNAVAILABLE"

    # Server Errors (500)
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"
    DATABASE_ERROR = "DATABASE_ERROR"
    BIGQUERY_ERROR = "BIGQUERY_ERROR"
    STORAGE_ERROR = "STORAGE_ERROR"


class ResponseMetadata(BaseModel):
    """Standard metadata included in all API responses."""

    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    request_id: str = Field(default_factory=lambda: str(uuid4()))
    version: str = Field(default="1.0.0")


class APIError(BaseModel):
    """Standard error structure for API responses."""

    code: ErrorCode
    message: str
    details: dict[str, Any] | None = None
    trace_id: str | None = None  # For OpenTelemetry correlation


class APIResponse(BaseModel, Generic[T]):
    """Standard API response envelope with generic data type."""

    success: bool
    data: T | None = None
    error: APIError | None = None
    metadata: ResponseMetadata = Field(default_factory=ResponseMetadata)


class ResponseFactory:
    """Factory class for creating standardized API responses."""

    @staticmethod
    def success(
        data: Any = None,
        request_id: str | None = None,
        trace_id: str | None = None,
    ) -> dict[str, Any]:
        """Create a successful API response.

        Args:
            data: Response data (any JSON-serializable type)
            request_id: Optional request ID override
            trace_id: Optional OpenTelemetry trace ID

        Returns:
            Dict with success=True and data
        """
        metadata = ResponseMetadata()
        if request_id:
            metadata.request_id = request_id

        response = APIResponse(success=True, data=data, metadata=metadata)
        result = response.model_dump(exclude_none=True)

        # Add trace_id to metadata if provided
        if trace_id:
            result["metadata"]["trace_id"] = trace_id

        return result

    @staticmethod
    def error(
        error_code: ErrorCode,
        message: str,
        details: dict[str, Any] | None = None,
        status_code: int = 400,
        request_id: str | None = None,
        trace_id: str | None = None,
    ) -> JSONResponse:
        """Create an error API response.

        Args:
            error_code: Error code enum
            message: Human-readable error message
            details: Additional error context
            status_code: HTTP status code
            request_id: Optional request ID override
            trace_id: Optional OpenTelemetry trace ID

        Returns:
            JSONResponse with error structure
        """
        metadata = ResponseMetadata()
        if request_id:
            metadata.request_id = request_id

        api_error = APIError(code=error_code, message=message, details=details, trace_id=trace_id)
        response = APIResponse(success=False, error=api_error, metadata=metadata)

        return JSONResponse(
            status_code=status_code, content=response.model_dump(exclude_none=True)
        )

    @staticmethod
    def validation_error(
        message: str,
        field: str | None = None,
        reason: str | None = None,
        trace_id: str | None = None,
    ) -> JSONResponse:
        """Create a validation error response.

        Args:
            message: Error message
            field: Field name that failed validation
            reason: Validation failure reason
            trace_id: Optional trace ID

        Returns:
            JSONResponse with 400 status
        """
        details = {}
        if field:
            details["field"] = field
        if reason:
            details["reason"] = reason

        return ResponseFactory.error(
            error_code=ErrorCode.VALIDATION_ERROR,
            message=message,
            details=details if details else None,
            status_code=400,
            trace_id=trace_id,
        )

    @staticmethod
    def not_found_error(
        resource_type: str,
        identifier: str,
        trace_id: str | None = None,
    ) -> JSONResponse:
        """Create a not found error response.

        Args:
            resource_type: Type of resource (dashboard, query, user)
            identifier: Resource identifier (slug, ID)
            trace_id: Optional trace ID

        Returns:
            JSONResponse with 404 status
        """
        return ResponseFactory.error(
            error_code=ErrorCode.DASHBOARD_NOT_FOUND
            if resource_type == "dashboard"
            else ErrorCode.QUERY_NOT_FOUND
            if resource_type == "query"
            else ErrorCode.USER_NOT_FOUND,
            message=f"{resource_type.title()} '{identifier}' not found",
            details={"resource_type": resource_type, "identifier": identifier},
            status_code=404,
            trace_id=trace_id,
        )

    @staticmethod
    def bigquery_error(
        message: str,
        bytes_scanned: int | None = None,
        query_hash: str | None = None,
        trace_id: str | None = None,
    ) -> JSONResponse:
        """Create a BigQuery execution error response.

        Args:
            message: Error message from BigQuery
            bytes_scanned: Bytes scanned before failure
            query_hash: Query hash for debugging
            trace_id: Optional trace ID

        Returns:
            JSONResponse with 422 status
        """
        details = {}
        if bytes_scanned is not None:
            details["bytes_scanned"] = bytes_scanned
        if query_hash:
            details["query_hash"] = query_hash

        return ResponseFactory.error(
            error_code=ErrorCode.BIGQUERY_ERROR,
            message=message,
            details=details if details else None,
            status_code=422,
            trace_id=trace_id,
        )

    @staticmethod
    def auth_required_error(
        message: str = "Authentication required",
        trace_id: str | None = None,
    ) -> JSONResponse:
        """Create an authentication required error.

        Args:
            message: Error message
            trace_id: Optional trace ID

        Returns:
            JSONResponse with 401 status
        """
        return ResponseFactory.error(
            error_code=ErrorCode.AUTHENTICATION_REQUIRED,
            message=message,
            status_code=401,
            trace_id=trace_id,
        )

    @staticmethod
    def forbidden_error(
        message: str = "Access forbidden",
        required_permission: str | None = None,
        trace_id: str | None = None,
    ) -> JSONResponse:
        """Create a forbidden error response.

        Args:
            message: Error message
            required_permission: Permission that was required
            trace_id: Optional trace ID

        Returns:
            JSONResponse with 403 status
        """
        details = {"required_permission": required_permission} if required_permission else None

        return ResponseFactory.error(
            error_code=ErrorCode.INSUFFICIENT_PERMISSIONS,
            message=message,
            details=details,
            status_code=403,
            trace_id=trace_id,
        )
