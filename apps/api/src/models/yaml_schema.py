"""
Pydantic models for dashboard YAML schema validation.
These models define the structure of dashboard YAML files.

PDR Reference: §4 (Data & Control Flows), §8 (User Journeys)

YAML Structure:
```yaml
metadata:
  slug: revenue-dashboard
  name: Revenue Dashboard
  owner: user@example.com
  view_type: analytical
  description: Revenue trends by region
  tags: [revenue, regional]

queries:
  - id: revenue_by_region
    warehouse: bigquery
    sql: |
      SELECT region, SUM(revenue) as total
      FROM `project.dataset.sales`
      WHERE date >= DATE_SUB(CURRENT_DATE(), INTERVAL 90 DAY)
      GROUP BY region

layout:
  - id: chart_1
    type: bar_chart
    chart:
      title: Revenue by Region
      x_axis: region
      y_axis: total
      color: region
    query_ref: revenue_by_region
    position:
      x: 0
      y: 0
      w: 6
      h: 4
```
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field, field_validator, model_validator


# =============================================================================
# Enums
# =============================================================================


class ViewType(str, Enum):
    """Dashboard view type (PDR §8)."""

    analytical = "analytical"
    operational = "operational"
    strategic = "strategic"


class WarehouseType(str, Enum):
    """Data warehouse type."""

    bigquery = "bigquery"


class ChartType(str, Enum):
    """Supported chart types."""

    line_chart = "line_chart"
    bar_chart = "bar_chart"
    area_chart = "area_chart"
    table = "table"
    kpi = "kpi"


# =============================================================================
# Metadata
# =============================================================================


class DashboardMetadata(BaseModel):
    """Dashboard metadata section."""

    slug: str = Field(
        ...,
        description="URL-safe dashboard identifier",
        pattern=r"^[a-z0-9][a-z0-9-]*[a-z0-9]$",
        min_length=3,
        max_length=100,
    )
    name: str = Field(..., description="Human-readable dashboard name", min_length=1, max_length=255)
    owner: str = Field(..., description="Owner email address")
    view_type: ViewType = Field(default=ViewType.analytical, description="Dashboard view type")
    description: Optional[str] = Field(default=None, description="Dashboard description")
    tags: List[str] = Field(default_factory=list, description="Dashboard tags")

    # Phase 6: YAML as Single Source of Truth - Additional metadata fields
    owner_email: str = Field(..., description="Owner email address (replaces owner_id)")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    access_count: int = Field(default=0, description="Number of times dashboard has been accessed")
    last_accessed: Optional[datetime] = Field(default=None, description="Last access timestamp")

    @field_validator("owner")
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Validate owner email format."""
        if "@" not in v:
            raise ValueError("Owner must be a valid email address")
        return v.lower()

    @field_validator("owner_email")
    @classmethod
    def validate_owner_email(cls, v: str) -> str:
        """Validate owner_email format."""
        if "@" not in v:
            raise ValueError("Owner email must be a valid email address")
        return v.lower()

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v: List[str]) -> List[str]:
        """Validate and normalize tags."""
        # Remove duplicates and normalize
        return list(set(tag.lower().strip() for tag in v if tag.strip()))


# =============================================================================
# Queries
# =============================================================================


class Query(BaseModel):
    """Query definition."""

    id: str = Field(
        ...,
        description="Unique query identifier within dashboard",
        pattern=r"^[a-z0-9_]+$",
        min_length=1,
        max_length=100,
    )
    warehouse: WarehouseType = Field(default=WarehouseType.bigquery, description="Data warehouse")
    sql: str = Field(..., description="SQL query", min_length=10)
    max_bytes_billed: Optional[int] = Field(
        default=None,
        description="Override max bytes billed for this query",
        gt=0,
    )

    @field_validator("sql")
    @classmethod
    def validate_sql(cls, v: str) -> str:
        """Validate SQL is not empty and trim whitespace."""
        sql = v.strip()
        if not sql:
            raise ValueError("SQL query cannot be empty")
        return sql


# =============================================================================
# Chart Configuration
# =============================================================================


class ChartConfig(BaseModel):
    """Base chart configuration."""

    title: str = Field(..., description="Chart title", min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, description="Chart description")


class AxisConfig(BaseModel):
    """Axis configuration for charts."""

    field: str = Field(..., description="Field name from query results")
    label: Optional[str] = Field(default=None, description="Axis label")
    format: Optional[str] = Field(default=None, description="Value format (e.g., ',.0f', '.2%')")


class LineChartConfig(ChartConfig):
    """Line chart configuration."""

    x_axis: Union[str, AxisConfig] = Field(..., description="X-axis configuration")
    y_axis: Union[str, AxisConfig] = Field(..., description="Y-axis configuration")
    color: Optional[str] = Field(default=None, description="Color dimension field")
    show_points: bool = Field(default=True, description="Show data points")
    show_legend: bool = Field(default=True, description="Show legend")


class BarChartConfig(ChartConfig):
    """Bar chart configuration."""

    x_axis: Union[str, AxisConfig] = Field(..., description="X-axis (category) configuration")
    y_axis: Union[str, AxisConfig] = Field(..., description="Y-axis (value) configuration")
    color: Optional[str] = Field(default=None, description="Color dimension field")
    orientation: Literal["vertical", "horizontal"] = Field(
        default="vertical", description="Bar orientation"
    )
    show_legend: bool = Field(default=True, description="Show legend")


class AreaChartConfig(ChartConfig):
    """Area chart configuration."""

    x_axis: Union[str, AxisConfig] = Field(..., description="X-axis configuration")
    y_axis: Union[str, AxisConfig] = Field(..., description="Y-axis configuration")
    color: Optional[str] = Field(default=None, description="Color dimension field")
    stacked: bool = Field(default=False, description="Stack areas")
    show_legend: bool = Field(default=True, description="Show legend")


class TableConfig(ChartConfig):
    """Table chart configuration."""

    columns: List[str] = Field(..., description="Column names to display", min_length=1)
    sortable: bool = Field(default=True, description="Enable column sorting")
    filterable: bool = Field(default=False, description="Enable column filtering")
    page_size: int = Field(default=10, description="Rows per page", gt=0, le=100)


class KPIConfig(ChartConfig):
    """KPI tile configuration."""

    value_field: str = Field(..., description="Field containing KPI value")
    format: Optional[str] = Field(default=None, description="Value format (e.g., ',.0f', '.2%')")
    trend_field: Optional[str] = Field(default=None, description="Field for trend indicator")
    comparison_field: Optional[str] = Field(
        default=None, description="Field for comparison (e.g., previous period)"
    )


# =============================================================================
# Layout
# =============================================================================


class GridPosition(BaseModel):
    """Grid position for layout (12-column grid)."""

    x: int = Field(..., description="X position (0-11)", ge=0, lt=12)
    y: int = Field(..., description="Y position (row)", ge=0)
    w: int = Field(..., description="Width (1-12)", ge=1, le=12)
    h: int = Field(..., description="Height (rows)", ge=1, le=20)

    @model_validator(mode="after")
    def validate_position(self) -> "GridPosition":
        """Validate grid position doesn't exceed bounds."""
        if self.x + self.w > 12:
            raise ValueError(f"Position x({self.x}) + width({self.w}) exceeds grid width of 12")
        return self


class LayoutItem(BaseModel):
    """Layout item definition."""

    id: str = Field(
        ...,
        description="Unique chart identifier",
        pattern=r"^[a-z0-9_]+$",
        min_length=1,
        max_length=100,
    )
    type: ChartType = Field(..., description="Chart type")
    chart: Union[
        LineChartConfig,
        BarChartConfig,
        AreaChartConfig,
        TableConfig,
        KPIConfig,
    ] = Field(..., description="Chart configuration")
    query_ref: str = Field(..., description="Reference to query ID")
    position: GridPosition = Field(..., description="Grid position")
    style: Optional[Dict[str, Any]] = Field(default=None, description="Custom CSS styles")

    @field_validator("chart", mode="before")
    @classmethod
    def validate_chart_config(cls, v: Any, info) -> Any:
        """Validate chart config matches type."""
        # Let Pydantic's discriminated union handle this
        return v


# =============================================================================
# Root Dashboard Schema
# =============================================================================


class DashboardYAML(BaseModel):
    """Root dashboard YAML schema."""

    metadata: DashboardMetadata = Field(..., description="Dashboard metadata")
    queries: List[Query] = Field(..., description="Query definitions", min_length=1)
    layout: List[LayoutItem] = Field(..., description="Layout items", min_length=1)

    @model_validator(mode="after")
    def validate_query_refs(self) -> "DashboardYAML":
        """Validate all query_refs exist in queries."""
        query_ids = {q.id for q in self.queries}
        for item in self.layout:
            if item.query_ref not in query_ids:
                raise ValueError(
                    f"Chart '{item.id}' references unknown query '{item.query_ref}'. "
                    f"Available queries: {', '.join(sorted(query_ids))}"
                )
        return self

    @model_validator(mode="after")
    def validate_chart_ids_unique(self) -> "DashboardYAML":
        """Validate all chart IDs are unique."""
        chart_ids = [item.id for item in self.layout]
        duplicates = {id for id in chart_ids if chart_ids.count(id) > 1}
        if duplicates:
            raise ValueError(f"Duplicate chart IDs found: {', '.join(sorted(duplicates))}")
        return self

    @model_validator(mode="after")
    def validate_query_ids_unique(self) -> "DashboardYAML":
        """Validate all query IDs are unique."""
        query_ids = [q.id for q in self.queries]
        duplicates = {id for id in query_ids if query_ids.count(id) > 1}
        if duplicates:
            raise ValueError(f"Duplicate query IDs found: {', '.join(sorted(duplicates))}")
        return self

    @model_validator(mode="after")
    def validate_grid_overlaps(self) -> "DashboardYAML":
        """Validate no grid position overlaps (PDR §8)."""
        positions = []
        for item in self.layout:
            pos = item.position
            for x in range(pos.x, pos.x + pos.w):
                for y in range(pos.y, pos.y + pos.h):
                    if (x, y) in positions:
                        raise ValueError(
                            f"Chart '{item.id}' overlaps with another chart at position ({x}, {y})"
                        )
                    positions.append((x, y))
        return self


# =============================================================================
# API Response Models (separate from YAML schema)
# =============================================================================


class ValidationError(BaseModel):
    """Validation error detail."""

    field: str = Field(..., description="Field path with error")
    message: str = Field(..., description="Error message")
    type: str = Field(..., description="Error type")


class YAMLValidationResponse(BaseModel):
    """Response from YAML validation."""

    valid: bool = Field(..., description="Whether YAML is valid")
    errors: List[ValidationError] = Field(default_factory=list, description="Validation errors")
    warnings: List[str] = Field(default_factory=list, description="Validation warnings")
    parsed: Optional[DashboardYAML] = Field(default=None, description="Parsed dashboard if valid")


class CompilationResult(BaseModel):
    """Result from dashboard compilation (PDR §4)."""

    dashboard_slug: str = Field(..., description="Dashboard slug")
    execution_plan: Dict[str, Any] = Field(..., description="Query execution plan")
    query_count: int = Field(..., description="Number of queries")
    lineage_nodes: List[Dict[str, str]] = Field(..., description="Lineage node seeds")
    lineage_edges: List[Dict[str, str]] = Field(..., description="Lineage edge seeds")
    compiled_at: datetime = Field(default_factory=datetime.utcnow, description="Compilation timestamp")


class SQLVerificationResult(BaseModel):
    """Result from SQL verification (PDR §4)."""

    valid: bool = Field(..., description="Whether SQL is valid")
    job_id: Optional[str] = Field(default=None, description="BigQuery job ID")
    schema: List[Dict[str, str]] = Field(default_factory=list, description="Result schema")
    row_count: int = Field(default=0, description="Total row count")
    sample_rows: List[Dict[str, Any]] = Field(default_factory=list, description="Sample rows (max 100)")
    bytes_scanned: int = Field(default=0, description="Bytes scanned")
    bytes_billed: int = Field(default=0, description="Bytes billed")
    cache_hit: bool = Field(default=False, description="Whether query hit cache")
    duration_ms: int = Field(default=0, description="Execution duration in milliseconds")
    error: Optional[str] = Field(default=None, description="Error message if failed")
