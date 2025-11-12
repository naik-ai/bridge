"""
Onboarding API endpoints for team creation, connections, and catalog discovery.
"""

import logging
from typing import Any, Dict, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.auth import get_current_user
from ...core.database import get_db
from ...models.db_models import (
    CatalogJobStatus,
    Connection,
    ConnectionStatus,
    ConnectionType,
    Dataset,
    Table,
    Team,
    User,
)
from ...services.catalog import CatalogService, get_catalog_service
from ...services.connection import ConnectionService, get_connection_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/onboarding", tags=["onboarding"])


# Request/Response Models

class TeamCreate(BaseModel):
    """Request model for creating a team."""
    name: str = Field(..., min_length=1, max_length=255)
    slug: str = Field(..., min_length=1, max_length=255, pattern="^[a-z0-9-]+$")


class TeamResponse(BaseModel):
    """Response model for team."""
    id: UUID
    name: str
    slug: str
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class ConnectionCreate(BaseModel):
    """Request model for creating a connection."""
    team_id: UUID
    name: str = Field(..., min_length=1, max_length=255)
    connection_type: ConnectionType
    credentials: Dict[str, Any] = Field(..., description="Unencrypted credentials")


class ConnectionResponse(BaseModel):
    """Response model for connection."""
    id: UUID
    team_id: UUID
    name: str
    connection_type: ConnectionType
    status: ConnectionStatus
    last_tested_at: str | None
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class DatasetResponse(BaseModel):
    """Response model for dataset."""
    id: UUID
    connection_id: UUID
    name: str
    fully_qualified_name: str
    description: str | None
    catalog_job_status: CatalogJobStatus
    discovered_at: str
    last_scanned_at: str | None

    class Config:
        from_attributes = True


class TableColumn(BaseModel):
    """Schema column definition."""
    name: str
    type: str
    nullable: bool | None = None
    description: str | None = None


class TableResponse(BaseModel):
    """Response model for table."""
    id: UUID
    dataset_id: UUID
    name: str
    fully_qualified_name: str
    description: str | None
    schema: List[TableColumn] | None
    row_count: int | None
    size_bytes: int | None
    discovered_at: str
    last_scanned_at: str | None

    class Config:
        from_attributes = True


class CatalogScanRequest(BaseModel):
    """Request model for catalog scan."""
    dataset_id: UUID


class CatalogScanResponse(BaseModel):
    """Response model for catalog scan."""
    dataset_id: UUID
    status: CatalogJobStatus
    tables_found: int


# Team Endpoints

@router.post("/teams", response_model=TeamResponse, status_code=status.HTTP_201_CREATED)
async def create_team(
    team_data: TeamCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new team.

    Args:
        team_data: Team creation data
        current_user: Authenticated user
        db: Database session

    Returns:
        Created team

    Raises:
        HTTPException: If team slug already exists
    """
    # Check if slug exists
    result = await db.execute(select(Team).where(Team.slug == team_data.slug))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Team with slug '{team_data.slug}' already exists",
        )

    # Create team
    team = Team(name=team_data.name, slug=team_data.slug)
    db.add(team)
    await db.commit()
    await db.refresh(team)

    logger.info(f"User {current_user.email} created team {team.id}")
    return team


@router.get("/teams", response_model=List[TeamResponse])
async def list_teams(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all teams.

    Args:
        current_user: Authenticated user
        db: Database session

    Returns:
        List of teams
    """
    result = await db.execute(select(Team))
    teams = result.scalars().all()
    return list(teams)


@router.get("/teams/{team_id}", response_model=TeamResponse)
async def get_team(
    team_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get team by ID.

    Args:
        team_id: Team ID
        current_user: Authenticated user
        db: Database session

    Returns:
        Team

    Raises:
        HTTPException: If team not found
    """
    team = await db.get(Team, team_id)
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Team {team_id} not found",
        )
    return team


# Connection Endpoints

@router.post("/connections", response_model=ConnectionResponse, status_code=status.HTTP_201_CREATED)
async def create_connection(
    connection_data: ConnectionCreate,
    current_user: User = Depends(get_current_user),
    connection_service: ConnectionService = Depends(get_connection_service),
):
    """Create a new database connection.

    Args:
        connection_data: Connection creation data
        current_user: Authenticated user
        connection_service: Connection service

    Returns:
        Created connection

    Raises:
        HTTPException: If team not found or credentials invalid
    """
    try:
        connection = await connection_service.create_connection(
            team_id=connection_data.team_id,
            name=connection_data.name,
            connection_type=connection_data.connection_type,
            credentials=connection_data.credentials,
        )

        logger.info(f"User {current_user.email} created connection {connection.id}")
        return connection

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/connections", response_model=List[ConnectionResponse])
async def list_connections(
    team_id: UUID,
    current_user: User = Depends(get_current_user),
    connection_service: ConnectionService = Depends(get_connection_service),
):
    """List all connections for a team.

    Args:
        team_id: Team ID
        current_user: Authenticated user
        connection_service: Connection service

    Returns:
        List of connections
    """
    connections = await connection_service.list_connections(team_id)
    return connections


@router.get("/connections/{connection_id}", response_model=ConnectionResponse)
async def get_connection(
    connection_id: UUID,
    current_user: User = Depends(get_current_user),
    connection_service: ConnectionService = Depends(get_connection_service),
):
    """Get connection by ID.

    Args:
        connection_id: Connection ID
        current_user: Authenticated user
        connection_service: Connection service

    Returns:
        Connection

    Raises:
        HTTPException: If connection not found
    """
    connection = await connection_service.get_connection(connection_id)
    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Connection {connection_id} not found",
        )
    return connection


@router.post("/connections/{connection_id}/test", response_model=ConnectionResponse)
async def test_connection(
    connection_id: UUID,
    current_user: User = Depends(get_current_user),
    connection_service: ConnectionService = Depends(get_connection_service),
):
    """Test a database connection.

    Args:
        connection_id: Connection ID
        current_user: Authenticated user
        connection_service: Connection service

    Returns:
        Updated connection with status

    Raises:
        HTTPException: If connection not found
    """
    try:
        success = await connection_service.test_connection(connection_id)
        connection = await connection_service.get_connection(connection_id)

        if not success:
            logger.warning(f"Connection test failed for {connection_id}")

        return connection

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.delete("/connections/{connection_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_connection(
    connection_id: UUID,
    current_user: User = Depends(get_current_user),
    connection_service: ConnectionService = Depends(get_connection_service),
):
    """Delete a connection.

    Args:
        connection_id: Connection ID
        current_user: Authenticated user
        connection_service: Connection service

    Raises:
        HTTPException: If connection not found
    """
    try:
        await connection_service.delete_connection(connection_id)
        logger.info(f"User {current_user.email} deleted connection {connection_id}")

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


# Catalog Discovery Endpoints

@router.post("/catalog/discover", response_model=List[DatasetResponse])
async def discover_datasets(
    connection_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    connection_service: ConnectionService = Depends(get_connection_service),
    catalog_service: CatalogService = Depends(get_catalog_service),
):
    """Discover all datasets/schemas from a connection.

    Args:
        connection_id: Connection ID
        current_user: Authenticated user
        db: Database session
        connection_service: Connection service
        catalog_service: Catalog service

    Returns:
        List of discovered datasets

    Raises:
        HTTPException: If connection not found
    """
    try:
        datasets = await catalog_service.discover_datasets(connection_id)
        logger.info(f"Discovered {len(datasets)} datasets for connection {connection_id}")
        return datasets

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.post("/catalog/scan", response_model=CatalogScanResponse)
async def scan_dataset(
    scan_request: CatalogScanRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    connection_service: ConnectionService = Depends(get_connection_service),
    catalog_service: CatalogService = Depends(get_catalog_service),
):
    """Scan all tables in a dataset.

    Args:
        scan_request: Catalog scan request
        current_user: Authenticated user
        db: Database session
        connection_service: Connection service
        catalog_service: Catalog service

    Returns:
        Scan result

    Raises:
        HTTPException: If dataset not found or scan fails
    """
    try:
        tables = await catalog_service.scan_dataset_tables(scan_request.dataset_id)

        # Get updated dataset status
        dataset = await db.get(Dataset, scan_request.dataset_id)

        logger.info(f"Scanned {len(tables)} tables in dataset {scan_request.dataset_id}")

        return CatalogScanResponse(
            dataset_id=scan_request.dataset_id,
            status=dataset.catalog_job_status,
            tables_found=len(tables),
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Catalog scan failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Catalog scan failed",
        )


@router.get("/catalog/datasets/{dataset_id}/tables", response_model=List[TableResponse])
async def get_dataset_tables(
    dataset_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    connection_service: ConnectionService = Depends(get_connection_service),
    catalog_service: CatalogService = Depends(get_catalog_service),
):
    """Get all tables for a dataset.

    Args:
        dataset_id: Dataset ID
        current_user: Authenticated user
        db: Database session
        connection_service: Connection service
        catalog_service: Catalog service

    Returns:
        List of tables
    """
    tables = await catalog_service.get_dataset_tables(dataset_id)
    return tables


@router.get("/catalog/tables/{table_id}/schema", response_model=List[TableColumn])
async def get_table_schema(
    table_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    connection_service: ConnectionService = Depends(get_connection_service),
    catalog_service: CatalogService = Depends(get_catalog_service),
):
    """Get table schema.

    Args:
        table_id: Table ID
        current_user: Authenticated user
        db: Database session
        connection_service: Connection service
        catalog_service: Catalog service

    Returns:
        Table schema

    Raises:
        HTTPException: If table not found
    """
    schema = await catalog_service.get_table_schema(table_id)
    if not schema:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Table {table_id} not found",
        )
    return schema
