"""
Dashboard lifecycle endpoints for Peter Dashboard Platform.
Handles validate, compile, save, list, and get operations.

PDR Reference: §4 (Data & Control Flows), §8 (User Journeys), §11 (Acceptance Criteria)
"""

from typing import List, Optional

import structlog
import yaml
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field

from src.core.dependencies import (
    get_current_user,
    get_dashboard_compiler_service,
    get_storage_service,
    get_yaml_validation_service,
)
from src.core.exceptions import (
    CompilationException,
    DashboardAlreadyExistsException,
    DashboardNotFoundException,
    YAMLValidationException,
)
from src.core.response import ErrorCode, ResponseFactory
from src.models.db_models import Dashboard, User
from src.models.yaml_schema import (
    CompilationResult,
    DashboardYAML,
    YAMLValidationResponse,
)
from src.services.dashboard_compiler import DashboardCompilerService
from src.services.storage import StorageService
from src.services.yaml_validation import YAMLValidationService

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/dashboards", tags=["Dashboards"])


# =============================================================================
# Request/Response Models
# =============================================================================


class ValidateRequest(BaseModel):
    """Request model for YAML validation."""

    yaml_content: str = Field(..., description="Dashboard YAML content to validate")
    validate_sql: bool = Field(default=True, description="Whether to validate SQL via BigQuery dry run")


class CompileRequest(BaseModel):
    """Request model for dashboard compilation."""

    yaml_content: str = Field(..., description="Dashboard YAML content to compile")


class SaveRequest(BaseModel):
    """Request model for saving dashboard."""

    yaml_content: str = Field(..., description="Dashboard YAML content to save")
    overwrite: bool = Field(default=False, description="Whether to overwrite existing dashboard")


class DashboardListItem(BaseModel):
    """Dashboard list item response."""

    id: str
    slug: str
    name: str
    description: Optional[str]
    view_type: str
    tags: Optional[List[str]]
    owner_email: str
    version: int
    created_at: str
    updated_at: str
    access_count: int


class DashboardDetail(BaseModel):
    """Detailed dashboard response."""

    id: str
    slug: str
    name: str
    description: Optional[str]
    view_type: str
    tags: Optional[List[str]]
    owner_id: str
    owner_email: str
    storage_path: str
    version: int
    created_at: str
    updated_at: str
    last_accessed: Optional[str]
    access_count: int


class PaginatedDashboards(BaseModel):
    """Paginated dashboard list response."""

    dashboards: List[DashboardListItem]
    total: int
    page: int
    page_size: int
    has_next: bool


# =============================================================================
# Endpoints
# =============================================================================


@router.post("/validate")
async def validate_dashboard(
    request: ValidateRequest,
    validation_service: YAMLValidationService = Depends(get_yaml_validation_service),
    user: User = Depends(get_current_user),
) -> dict:
    """
    Validate dashboard YAML.

    PDR §4: "Dashboard validate endpoint rejects invalid YAML with specific error messages"
    PDR §11 Acceptance: "Dashboard validate endpoint rejects invalid YAML with specific error messages"

    Validation stages:
    1. Parse YAML syntax
    2. Validate against Pydantic schema
    3. Check query references
    4. Validate grid layout (no overlaps)
    5. Optional: Dry-run SQL queries in BigQuery

    Args:
        request: Validation request with YAML content
        validation_service: YAML validation service
        user: Current authenticated user

    Returns:
        Validation response with errors or success
    """
    try:
        logger.info("validating_dashboard_yaml", user_id=str(user.id))

        result = await validation_service.validate_yaml_string(
            yaml_content=request.yaml_content,
            validate_sql=request.validate_sql,
        )

        if result.valid:
            logger.info("yaml_validation_successful")
            return ResponseFactory.success(
                data={
                    "valid": True,
                    "dashboard": result.parsed.model_dump() if result.parsed else None,
                    "warnings": result.warnings,
                }
            )
        else:
            logger.warning("yaml_validation_failed", error_count=len(result.errors))
            return ResponseFactory.success(
                data={
                    "valid": False,
                    "errors": [error.model_dump() for error in result.errors],
                    "warnings": result.warnings,
                }
            )

    except Exception as e:
        logger.error("validation_failed", error=str(e))
        return ResponseFactory.error(
            error_code=ErrorCode.VALIDATION_ERROR,
            message=f"Validation failed: {str(e)}",
            status_code=400,
        )


@router.post("/compile")
async def compile_dashboard(
    request: CompileRequest,
    validation_service: YAMLValidationService = Depends(get_yaml_validation_service),
    compiler_service: DashboardCompilerService = Depends(get_dashboard_compiler_service),
    user: User = Depends(get_current_user),
) -> dict:
    """
    Compile dashboard YAML to execution plan.

    PDR §4: "Dashboard compile endpoint returns execution plan with query list and lineage seeds"
    PDR §11 Acceptance: "Dashboard compile endpoint returns execution plan with query list and lineage seeds"

    Args:
        request: Compilation request with YAML content
        validation_service: YAML validation service
        compiler_service: Dashboard compiler service
        user: Current authenticated user

    Returns:
        Compilation result with execution plan and lineage seeds
    """
    try:
        logger.info("compiling_dashboard", user_id=str(user.id))

        # First validate YAML
        validation_result = await validation_service.validate_yaml_string(
            yaml_content=request.yaml_content,
            validate_sql=False,  # Skip SQL validation for compilation
        )

        if not validation_result.valid:
            logger.warning("compilation_failed_validation", error_count=len(validation_result.errors))
            return ResponseFactory.error(
                error_code=ErrorCode.INVALID_YAML,
                message="Cannot compile invalid YAML",
                details={
                    "errors": [error.model_dump() for error in validation_result.errors],
                },
                status_code=400,
            )

        # Compile dashboard
        compilation_result = await compiler_service.compile_dashboard(validation_result.parsed)

        logger.info(
            "dashboard_compiled",
            slug=compilation_result.dashboard_slug,
            query_count=compilation_result.query_count,
        )

        return ResponseFactory.success(data=compilation_result.model_dump())

    except CompilationException as e:
        logger.error("compilation_failed", error=str(e))
        return ResponseFactory.error(
            error_code=ErrorCode.VALIDATION_ERROR,
            message=str(e),
            details=e.details,
            status_code=400,
        )

    except Exception as e:
        logger.error("compilation_error", error=str(e))
        return ResponseFactory.error(
            error_code=ErrorCode.INTERNAL_SERVER_ERROR,
            message=f"Compilation failed: {str(e)}",
            status_code=500,
        )


@router.post("/save")
async def save_dashboard(
    request: SaveRequest,
    validation_service: YAMLValidationService = Depends(get_yaml_validation_service),
    storage_service: StorageService = Depends(get_storage_service),
    user: User = Depends(get_current_user),
) -> dict:
    """
    Save dashboard YAML to storage.

    PDR §4: "Dashboard save writes YAML to storage and updates Postgres index"
    PDR §11 Acceptance: "Dashboard save writes YAML to storage and creates index entry in Postgres"

    Flow:
    1. Validate YAML
    2. Write YAML to storage (filesystem for MVP)
    3. Create/update index entry in Postgres
    4. Return success with dashboard metadata

    Args:
        request: Save request with YAML content
        validation_service: YAML validation service
        storage_service: Storage service
        user: Current authenticated user

    Returns:
        Dashboard metadata
    """
    try:
        logger.info("saving_dashboard", user_id=str(user.id))

        # Validate YAML first
        validation_result = await validation_service.validate_yaml_string(
            yaml_content=request.yaml_content,
            validate_sql=True,  # Full validation including SQL
        )

        if not validation_result.valid:
            logger.warning("save_failed_validation", error_count=len(validation_result.errors))
            return ResponseFactory.error(
                error_code=ErrorCode.INVALID_YAML,
                message="Cannot save invalid YAML",
                details={
                    "errors": [error.model_dump() for error in validation_result.errors],
                },
                status_code=400,
            )

        # Save to storage (Phase 6: Returns DashboardYAML, not DB model)
        saved_dashboard = await storage_service.save_dashboard(
            dashboard_yaml=validation_result.parsed,
            owner_email=user.email,
            overwrite=request.overwrite,
        )

        logger.info(
            "dashboard_saved",
            slug=saved_dashboard.metadata.slug,
        )

        return ResponseFactory.success(
            data={
                "slug": saved_dashboard.metadata.slug,
                "name": saved_dashboard.metadata.name,
                "owner_email": saved_dashboard.metadata.owner_email,
                "storage_path": str(storage_service._get_file_path(saved_dashboard.metadata.slug)),
                "created_at": saved_dashboard.metadata.created_at.isoformat(),
                "updated_at": saved_dashboard.metadata.updated_at.isoformat(),
            }
        )

    except DashboardAlreadyExistsException as e:
        logger.warning("dashboard_already_exists", error=str(e))
        return ResponseFactory.error(
            error_code=ErrorCode.VALIDATION_ERROR,
            message=str(e),
            details=e.details,
            status_code=409,  # Conflict
        )

    except YAMLValidationException as e:
        logger.error("save_validation_failed", error=str(e))
        return ResponseFactory.error(
            error_code=ErrorCode.INVALID_YAML,
            message=str(e),
            details=e.details,
            status_code=400,
        )

    except Exception as e:
        logger.error("save_failed", error=str(e))
        return ResponseFactory.error(
            error_code=ErrorCode.STORAGE_ERROR,
            message=f"Failed to save dashboard: {str(e)}",
            status_code=500,
        )


@router.get("")
async def list_dashboards(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    view_type: Optional[str] = Query(None, description="Filter by view type"),
    tag: Optional[str] = Query(None, description="Filter by tag"),
    storage_service: StorageService = Depends(get_storage_service),
    user: User = Depends(get_current_user),
) -> dict:
    """
    List dashboards with pagination.

    PDR §11 Acceptance: "Get dashboards endpoint returns list with pagination"

    Args:
        page: Page number (1-indexed)
        page_size: Items per page (max 100)
        view_type: Optional filter by view type
        tag: Optional filter by tag
        storage_service: Storage service
        user: Current authenticated user

    Returns:
        Paginated dashboard list
    """
    try:
        logger.info("listing_dashboards", page=page, page_size=page_size, user_id=str(user.id))

        dashboards, total = await storage_service.list_dashboards(
            page=page,
            page_size=page_size,
            view_type=view_type,
            tag=tag,
        )

        has_next = (page * page_size) < total

        # Phase 6: dashboards is now List[dict] from index, not DB models
        dashboard_list = [
            DashboardListItem(
                id=d.get("slug"),  # Using slug as ID since no DB
                slug=d.get("slug"),
                name=d.get("name"),
                description=None,  # Not in index
                view_type=d.get("view_type"),
                tags=d.get("tags", []),
                owner_email=d.get("owner_email", "unknown"),
                version=1,  # Not tracked in Phase 6
                created_at=d.get("created_at"),
                updated_at=d.get("updated_at"),
                access_count=d.get("access_count", 0),
            )
            for d in dashboards
        ]

        result = PaginatedDashboards(
            dashboards=dashboard_list,
            total=total,
            page=page,
            page_size=page_size,
            has_next=has_next,
        )

        logger.info("dashboards_listed", count=len(dashboards), total=total)

        return ResponseFactory.success(data=result.model_dump())

    except Exception as e:
        logger.error("list_dashboards_failed", error=str(e))
        return ResponseFactory.error(
            error_code=ErrorCode.DATABASE_ERROR,
            message=f"Failed to list dashboards: {str(e)}",
            status_code=500,
        )


@router.get("/{slug}")
async def get_dashboard(
    slug: str,
    storage_service: StorageService = Depends(get_storage_service),
    user: User = Depends(get_current_user),
) -> dict:
    """
    Get dashboard metadata by slug.

    PDR §11 Acceptance: "Get dashboards/{slug} endpoint returns dashboard metadata"

    Args:
        slug: Dashboard slug identifier
        storage_service: Storage service
        user: Current authenticated user

    Returns:
        Dashboard metadata
    """
    try:
        logger.info("getting_dashboard", slug=slug, user_id=str(user.id))

        # Phase 6: Load YAML directly, no DB lookup
        if not await storage_service.check_dashboard_exists(slug):
            logger.warning("dashboard_not_found", slug=slug)
            return ResponseFactory.not_found_error(resource_type="dashboard", identifier=slug)

        dashboard_yaml = await storage_service.load_dashboard_yaml(slug)

        # Update access stats
        await storage_service.record_access(slug)

        detail = DashboardDetail(
            id=dashboard_yaml.metadata.slug,  # Using slug as ID
            slug=dashboard_yaml.metadata.slug,
            name=dashboard_yaml.metadata.name,
            description=dashboard_yaml.metadata.description,
            view_type=dashboard_yaml.metadata.view_type.value,
            tags=dashboard_yaml.metadata.tags,
            owner_id=dashboard_yaml.metadata.owner_email,  # No separate owner_id in Phase 6
            owner_email=dashboard_yaml.metadata.owner_email,
            storage_path=str(storage_service._get_file_path(slug)),
            version=1,  # Not tracked in Phase 6
            created_at=dashboard_yaml.metadata.created_at.isoformat(),
            updated_at=dashboard_yaml.metadata.updated_at.isoformat(),
            last_accessed=(
                dashboard_yaml.metadata.last_accessed.isoformat()
                if dashboard_yaml.metadata.last_accessed
                else None
            ),
            access_count=dashboard_yaml.metadata.access_count,
        )

        logger.info("dashboard_retrieved", slug=slug)

        return ResponseFactory.success(data=detail.model_dump())

    except DashboardNotFoundException as e:
        logger.warning("dashboard_not_found", slug=slug)
        return ResponseFactory.not_found_error(resource_type="dashboard", identifier=slug)

    except Exception as e:
        logger.error("get_dashboard_failed", slug=slug, error=str(e))
        return ResponseFactory.error(
            error_code=ErrorCode.DATABASE_ERROR,
            message=f"Failed to get dashboard: {str(e)}",
            status_code=500,
        )


@router.post("/rebuild-index")
async def rebuild_index(
    storage_service: StorageService = Depends(get_storage_service),
    user: User = Depends(get_current_user),
) -> dict:
    """
    Rebuild dashboard index by scanning all YAML files.

    Phase 6: Maintenance endpoint for rebuilding .index.json file.
    Useful when index becomes corrupted or out of sync.

    Args:
        storage_service: Storage service
        user: Current authenticated user

    Returns:
        Rebuild statistics
    """
    try:
        logger.info("rebuilding_index", user_id=str(user.id))

        # Rebuild index
        await storage_service._rebuild_index()

        # Get stats
        stats = await storage_service.get_storage_stats()

        logger.info("index_rebuilt_successfully", dashboard_count=stats.get("index_entry_count"))

        return ResponseFactory.success(
            data={
                "dashboard_count": stats.get("index_entry_count"),
                "file_count": stats.get("file_count"),
                "generated_at": stats.get("generated_at"),
                "message": "Index rebuilt successfully",
            }
        )

    except Exception as e:
        logger.error("index_rebuild_failed", error=str(e))
        return ResponseFactory.error(
            error_code=ErrorCode.STORAGE_ERROR,
            message=f"Failed to rebuild index: {str(e)}",
            status_code=500,
        )
