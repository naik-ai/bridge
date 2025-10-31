"""
YAML Validation Service for dashboard definitions.
Validates YAML structure, query references, grid layout, and SQL syntax.

PDR Reference: §4 (Data & Control Flows), §8 (User Journeys), §11 (Acceptance Criteria)
"""

from typing import Any, Dict, List, Optional

import structlog
import yaml
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import YAMLValidationException
from src.integrations.bigquery_client import BigQueryClient
from src.models.yaml_schema import (
    DashboardYAML,
    ValidationError as SchemaValidationError,
    YAMLValidationResponse,
)

logger = structlog.get_logger(__name__)


class YAMLValidationService:
    """
    Service for validating dashboard YAML definitions.

    Validation stages:
    1. Parse YAML syntax
    2. Validate against Pydantic schema
    3. Check query references
    4. Validate grid layout (no overlaps)
    5. Optional: Dry-run SQL queries in BigQuery

    PDR §11 Acceptance: "Dashboard validate endpoint rejects invalid YAML with specific error messages"
    """

    def __init__(self, db: AsyncSession, bq_client: BigQueryClient):
        """
        Initialize YAML validation service.

        Args:
            db: Database session
            bq_client: BigQuery client for SQL validation
        """
        self.db = db
        self.bq_client = bq_client

    async def validate_yaml_string(
        self,
        yaml_content: str,
        validate_sql: bool = True,
    ) -> YAMLValidationResponse:
        """
        Validate dashboard YAML from string content.

        Args:
            yaml_content: YAML content as string
            validate_sql: Whether to validate SQL queries via BigQuery dry run

        Returns:
            YAMLValidationResponse with validation results

        Raises:
            YAMLValidationException: If validation fails critically
        """
        errors: List[SchemaValidationError] = []
        warnings: List[str] = []
        parsed_dashboard: Optional[DashboardYAML] = None

        # Stage 1: Parse YAML syntax
        try:
            yaml_dict = yaml.safe_load(yaml_content)
            if not isinstance(yaml_dict, dict):
                errors.append(
                    SchemaValidationError(
                        field="root",
                        message="YAML must be a dictionary/object",
                        type="type_error",
                    )
                )
                return YAMLValidationResponse(valid=False, errors=errors, warnings=warnings)

        except yaml.YAMLError as e:
            logger.warning("yaml_parse_failed", error=str(e))
            errors.append(
                SchemaValidationError(
                    field="root",
                    message=f"YAML syntax error: {str(e)}",
                    type="yaml_error",
                )
            )
            return YAMLValidationResponse(valid=False, errors=errors, warnings=warnings)

        # Stage 2: Validate against Pydantic schema
        try:
            parsed_dashboard = DashboardYAML.model_validate(yaml_dict)
            logger.info(
                "yaml_schema_validated",
                slug=parsed_dashboard.metadata.slug,
                query_count=len(parsed_dashboard.queries),
                chart_count=len(parsed_dashboard.layout),
            )

        except ValidationError as e:
            logger.warning("yaml_schema_validation_failed", error_count=len(e.errors()))

            for error in e.errors():
                # Convert Pydantic error to our format
                field_path = ".".join(str(loc) for loc in error["loc"])
                errors.append(
                    SchemaValidationError(
                        field=field_path,
                        message=error["msg"],
                        type=error["type"],
                    )
                )

            return YAMLValidationResponse(valid=False, errors=errors, warnings=warnings)

        # Stage 3: Validate SQL queries (optional)
        if validate_sql and parsed_dashboard:
            sql_errors = await self._validate_sql_queries(parsed_dashboard)
            errors.extend(sql_errors)

        # Stage 4: Additional warnings
        if parsed_dashboard:
            warnings.extend(self._check_warnings(parsed_dashboard))

        # Determine if valid
        is_valid = len(errors) == 0

        return YAMLValidationResponse(
            valid=is_valid,
            errors=errors,
            warnings=warnings,
            parsed=parsed_dashboard if is_valid else None,
        )

    async def validate_yaml_file(
        self,
        file_path: str,
        validate_sql: bool = True,
    ) -> YAMLValidationResponse:
        """
        Validate dashboard YAML from file.

        Args:
            file_path: Path to YAML file
            validate_sql: Whether to validate SQL queries

        Returns:
            YAMLValidationResponse with validation results
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                yaml_content = f.read()

            return await self.validate_yaml_string(yaml_content, validate_sql=validate_sql)

        except FileNotFoundError:
            logger.error("yaml_file_not_found", file_path=file_path)
            raise YAMLValidationException(
                message=f"YAML file not found: {file_path}",
                errors=[
                    {
                        "field": "file",
                        "message": f"File not found: {file_path}",
                        "type": "file_error",
                    }
                ],
            )
        except Exception as e:
            logger.error("yaml_file_read_failed", file_path=file_path, error=str(e))
            raise YAMLValidationException(
                message=f"Failed to read YAML file: {str(e)}",
                errors=[
                    {
                        "field": "file",
                        "message": str(e),
                        "type": "io_error",
                    }
                ],
            )

    async def _validate_sql_queries(
        self, dashboard: DashboardYAML
    ) -> List[SchemaValidationError]:
        """
        Validate SQL queries using BigQuery dry run.

        Args:
            dashboard: Parsed dashboard YAML

        Returns:
            List of validation errors for SQL queries
        """
        errors: List[SchemaValidationError] = []

        for query in dashboard.queries:
            try:
                # Use BigQuery's validate_query method
                is_valid, error_msg = self.bq_client.validate_query(query.sql)

                if not is_valid:
                    logger.warning(
                        "sql_validation_failed",
                        query_id=query.id,
                        error=error_msg,
                    )
                    errors.append(
                        SchemaValidationError(
                            field=f"queries.{query.id}.sql",
                            message=error_msg or "SQL validation failed",
                            type="sql_error",
                        )
                    )

            except Exception as e:
                logger.error(
                    "sql_validation_error",
                    query_id=query.id,
                    error=str(e),
                )
                errors.append(
                    SchemaValidationError(
                        field=f"queries.{query.id}.sql",
                        message=f"SQL validation error: {str(e)}",
                        type="sql_error",
                    )
                )

        return errors

    def _check_warnings(self, dashboard: DashboardYAML) -> List[str]:
        """
        Check for non-critical issues that should be warnings.

        Args:
            dashboard: Parsed dashboard YAML

        Returns:
            List of warning messages
        """
        warnings: List[str] = []

        # Check for large queries (potential performance issues)
        for query in dashboard.queries:
            if len(query.sql) > 10000:
                warnings.append(
                    f"Query '{query.id}' is very long ({len(query.sql)} characters). "
                    "Consider breaking into multiple queries or using views."
                )

        # Check for many charts (potential performance issues)
        if len(dashboard.layout) > 20:
            warnings.append(
                f"Dashboard has {len(dashboard.layout)} charts. "
                "Consider splitting into multiple dashboards for better performance."
            )

        # Check for unused queries
        used_query_refs = {item.query_ref for item in dashboard.layout}
        unused_queries = {q.id for q in dashboard.queries} - used_query_refs
        if unused_queries:
            warnings.append(
                f"Unused queries detected: {', '.join(sorted(unused_queries))}. "
                "Consider removing them to improve clarity."
            )

        # Check for overlapping tags
        if len(dashboard.metadata.tags) > 10:
            warnings.append(
                f"Dashboard has {len(dashboard.metadata.tags)} tags. "
                "Consider using fewer, more focused tags."
            )

        return warnings

    async def validate_and_parse(
        self,
        yaml_content: str,
        validate_sql: bool = True,
    ) -> DashboardYAML:
        """
        Validate YAML and return parsed dashboard or raise exception.

        Args:
            yaml_content: YAML content as string
            validate_sql: Whether to validate SQL queries

        Returns:
            Parsed DashboardYAML

        Raises:
            YAMLValidationException: If validation fails
        """
        result = await self.validate_yaml_string(yaml_content, validate_sql=validate_sql)

        if not result.valid:
            error_messages = [f"{e.field}: {e.message}" for e in result.errors]
            raise YAMLValidationException(
                message=f"YAML validation failed with {len(result.errors)} error(s)",
                errors=[e.model_dump() for e in result.errors],
            )

        if result.parsed is None:
            raise YAMLValidationException(
                message="YAML validation succeeded but no parsed result returned",
            )

        return result.parsed

    async def quick_validate(self, yaml_content: str) -> bool:
        """
        Quick validation without SQL checking (for rapid feedback).

        Args:
            yaml_content: YAML content as string

        Returns:
            True if valid, False otherwise
        """
        result = await self.validate_yaml_string(yaml_content, validate_sql=False)
        return result.valid

    def validate_slug_format(self, slug: str) -> tuple[bool, Optional[str]]:
        """
        Validate dashboard slug format.

        Args:
            slug: Dashboard slug

        Returns:
            Tuple of (is_valid, error_message)
        """
        import re

        # Must be lowercase alphanumeric with hyphens, 3-100 chars
        pattern = r"^[a-z0-9][a-z0-9-]*[a-z0-9]$"

        if not re.match(pattern, slug):
            return False, (
                "Slug must be lowercase alphanumeric with hyphens, "
                "start and end with alphanumeric, 3-100 characters"
            )

        if len(slug) < 3 or len(slug) > 100:
            return False, "Slug must be between 3 and 100 characters"

        # Check for reserved words
        reserved = {"admin", "api", "auth", "dashboard", "dashboards", "health", "docs"}
        if slug in reserved:
            return False, f"Slug '{slug}' is reserved and cannot be used"

        return True, None
