"""
Peter Dashboard Platform - FastAPI Application
Main entry point for the API service.

PDR Reference: Section 3 (Architecture Overview - API Service)
"""

import logging
import sys
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from src.api.v1.router import router as v1_router
from src.core.config import settings
from src.core.exceptions import (
    AuthenticationException,
    AuthorizationException,
    BigQueryException,
    DashboardNotFoundException,
    PeterException,
    ValidationException,
)
from src.core.response import ErrorCode, ResponseFactory


# =============================================================================
# Logging Configuration
# =============================================================================


def configure_logging():
    """Configure structured logging with structlog."""
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=logging.INFO,
    )

    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


# =============================================================================
# Application Lifecycle
# =============================================================================


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger = structlog.get_logger(__name__)

    # Startup
    logger.info("peter_api_starting", version="1.0.0", environment=settings.app_env)

    yield

    # Shutdown
    logger.info("peter_api_shutting_down")


# =============================================================================
# Application Creation
# =============================================================================


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    configure_logging()

    app = FastAPI(
        title="Peter Dashboard Platform API",
        description="Backend API for Peter Dashboard Platform with LLM-assisted authoring",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include v1 router
    app.include_router(v1_router)

    # Exception handlers
    register_exception_handlers(app)

    return app


# =============================================================================
# Exception Handlers
# =============================================================================


def register_exception_handlers(app: FastAPI):
    """Register global exception handlers."""
    logger = structlog.get_logger(__name__)

    @app.exception_handler(AuthenticationException)
    async def authentication_exception_handler(request: Request, exc: AuthenticationException):
        """Handle authentication exceptions."""
        logger.warning("authentication_exception", error=str(exc), path=request.url.path)
        return ResponseFactory.auth_required_error(message=str(exc))

    @app.exception_handler(AuthorizationException)
    async def authorization_exception_handler(request: Request, exc: AuthorizationException):
        """Handle authorization exceptions."""
        logger.warning("authorization_exception", error=str(exc), path=request.url.path)
        return ResponseFactory.forbidden_error(
            message=str(exc),
            required_permission=exc.details.get("required_permission"),
        )

    @app.exception_handler(ValidationException)
    async def validation_exception_handler(request: Request, exc: ValidationException):
        """Handle validation exceptions."""
        logger.warning("validation_exception", error=str(exc), path=request.url.path)
        return ResponseFactory.validation_error(
            message=str(exc),
            field=exc.details.get("field"),
            reason=exc.details.get("reason"),
        )

    @app.exception_handler(DashboardNotFoundException)
    async def dashboard_not_found_handler(request: Request, exc: DashboardNotFoundException):
        """Handle dashboard not found exceptions."""
        logger.warning("dashboard_not_found", error=str(exc), path=request.url.path)
        return ResponseFactory.not_found_error(
            resource_type="dashboard",
            identifier=exc.details.get("identifier", "unknown"),
        )

    @app.exception_handler(BigQueryException)
    async def bigquery_exception_handler(request: Request, exc: BigQueryException):
        """Handle BigQuery exceptions."""
        logger.error("bigquery_exception", error=str(exc), path=request.url.path)
        return ResponseFactory.bigquery_error(
            message=str(exc),
            bytes_scanned=exc.details.get("bytes_scanned"),
            query_hash=exc.details.get("query_hash"),
        )

    @app.exception_handler(PeterException)
    async def peter_exception_handler(request: Request, exc: PeterException):
        """Handle all Peter platform exceptions."""
        logger.error("peter_exception", error=str(exc), code=exc.error_code, path=request.url.path)
        return ResponseFactory.error(
            error_code=ErrorCode(exc.error_code) if exc.error_code in ErrorCode.__members__ else ErrorCode.INTERNAL_SERVER_ERROR,
            message=str(exc),
            details=exc.details,
            status_code=500,
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        """Handle unexpected exceptions."""
        logger.error(
            "unhandled_exception",
            error=str(exc),
            error_type=type(exc).__name__,
            path=request.url.path,
            exc_info=True,
        )
        return ResponseFactory.error(
            error_code=ErrorCode.INTERNAL_SERVER_ERROR,
            message="An unexpected error occurred",
            details={"error_type": type(exc).__name__},
            status_code=500,
        )


# =============================================================================
# Application Instance
# =============================================================================

app = create_app()


# =============================================================================
# Root Endpoint
# =============================================================================


@app.get("/")
async def root():
    """Root endpoint."""
    return ResponseFactory.success(
        data={
            "name": "Peter Dashboard Platform API",
            "version": "1.0.0",
            "status": "operational",
            "docs": "/docs",
            "health": "/v1/health",
        }
    )


# =============================================================================
# Application Runner
# =============================================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
