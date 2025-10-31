"""
SQLModel database models
SQLModel combines Pydantic validation with SQLAlchemy ORM.
"""

from datetime import datetime
from enum import Enum as PyEnum
from typing import List, Optional
from uuid import UUID, uuid4

import sqlalchemy
from sqlalchemy import Column, Index, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, Relationship, SQLModel


# Enums
class ViewType(str, PyEnum):
    """Dashboard view type."""
    analytical = "analytical"
    operational = "operational"
    strategic = "strategic"


class NodeType(str, PyEnum):
    """Lineage node type."""
    dashboard = "dashboard"
    chart = "chart"
    query = "query"
    table = "table"


class EdgeType(str, PyEnum):
    """Lineage edge type."""
    contains = "contains"
    executes = "executes"
    reads_from = "reads_from"


class QueryPurpose(str, PyEnum):
    """Query execution purpose."""
    verification = "verification"
    serving = "serving"
    precompute = "precompute"


# Database Models
class User(SQLModel, table=True):
    """User model for authentication."""

    __tablename__ = "users"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(max_length=255, unique=True, index=True, nullable=False)
    name: Optional[str] = Field(default=None, max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    last_login: Optional[datetime] = Field(default=None)
    is_active: bool = Field(default=True, nullable=False)

    # Relationships
    sessions: List["Session"] = Relationship(back_populates="user", cascade_delete=True)
    dashboards: List["Dashboard"] = Relationship(back_populates="owner")
    query_logs: List["QueryLog"] = Relationship(back_populates="user")


class Session(SQLModel, table=True):
    """Session model for authentication."""

    __tablename__ = "sessions"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", nullable=False, ondelete="CASCADE")
    token: str = Field(max_length=255, unique=True, index=True, nullable=False)
    expires_at: datetime = Field(nullable=False, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    last_accessed: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    user_agent: Optional[str] = Field(default=None, max_length=512)
    ip_address: Optional[str] = Field(default=None, max_length=45)  # IPv6 length

    # Relationships
    user: Optional[User] = Relationship(back_populates="sessions")


class Dashboard(SQLModel, table=True):
    """Dashboard model storing metadata and storage pointers."""

    __tablename__ = "dashboards"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    slug: str = Field(max_length=255, unique=True, index=True, nullable=False)
    name: str = Field(max_length=255, nullable=False)
    description: Optional[str] = Field(default=None, sa_column=Column(Text))
    owner_id: UUID = Field(foreign_key="users.id", nullable=False)

    # Storage reference
    storage_path: str = Field(max_length=512, nullable=False)
    version: int = Field(default=1, nullable=False)

    # Metadata
    view_type: ViewType = Field(default=ViewType.analytical, nullable=False)
    tags: Optional[List[str]] = Field(default=None, sa_column=Column(JSONB))

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    last_accessed: Optional[datetime] = Field(default=None)

    # Stats
    access_count: int = Field(default=0, nullable=False)

    # Relationships
    owner: Optional[User] = Relationship(back_populates="dashboards")
    query_logs: List["QueryLog"] = Relationship(back_populates="dashboard")

    __table_args__ = (
        Index("idx_dashboard_owner", "owner_id"),
        Index("idx_dashboard_updated", "updated_at"),
    )


class LineageNode(SQLModel, table=True):
    """Lineage node representing dashboard, chart, query, or table."""

    __tablename__ = "lineage_nodes"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    node_type: NodeType = Field(nullable=False)
    node_id: str = Field(max_length=255, nullable=False)

    # Node metadata as JSONB (renamed from 'metadata' to avoid SQLModel conflict)
    node_metadata: Optional[dict] = Field(default=None, sa_column=Column(JSONB))

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationships
    outgoing_edges: List["LineageEdge"] = Relationship(
        back_populates="source_node",
        sa_relationship_kwargs={"foreign_keys": "LineageEdge.source_node_id"},
        cascade_delete=True,
    )
    incoming_edges: List["LineageEdge"] = Relationship(
        back_populates="target_node",
        sa_relationship_kwargs={"foreign_keys": "LineageEdge.target_node_id"},
        cascade_delete=True,
    )

    __table_args__ = (
        UniqueConstraint("node_type", "node_id", name="uq_node_type_id"),
        Index("idx_lineage_node_type", "node_type"),
        Index("idx_lineage_node_id", "node_id"),
    )


class LineageEdge(SQLModel, table=True):
    """Lineage edge representing relationships between nodes."""

    __tablename__ = "lineage_edges"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    source_node_id: UUID = Field(foreign_key="lineage_nodes.id", nullable=False, ondelete="CASCADE")
    target_node_id: UUID = Field(foreign_key="lineage_nodes.id", nullable=False, ondelete="CASCADE")
    edge_type: EdgeType = Field(nullable=False)

    # Optional edge metadata (renamed from 'metadata' to avoid SQLModel conflict)
    edge_metadata: Optional[dict] = Field(default=None, sa_column=Column(JSONB))

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationships
    source_node: Optional[LineageNode] = Relationship(
        back_populates="outgoing_edges",
        sa_relationship_kwargs={"foreign_keys": "[LineageEdge.source_node_id]"},
    )
    target_node: Optional[LineageNode] = Relationship(
        back_populates="incoming_edges",
        sa_relationship_kwargs={"foreign_keys": "[LineageEdge.target_node_id]"},
    )

    __table_args__ = (
        UniqueConstraint("source_node_id", "target_node_id", "edge_type", name="uq_lineage_edge"),
        Index("idx_lineage_edge_source", "source_node_id"),
        Index("idx_lineage_edge_target", "target_node_id"),
        Index("idx_lineage_edge_type", "edge_type"),
    )


class QueryLog(SQLModel, table=True):
    """Query execution log for cost tracking and analytics."""

    __tablename__ = "query_logs"

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    # References
    dashboard_id: Optional[UUID] = Field(default=None, foreign_key="dashboards.id")
    user_id: Optional[UUID] = Field(default=None, foreign_key="users.id")

    # Query identification
    query_hash: str = Field(max_length=64, nullable=False, index=True)
    sql_preview: Optional[str] = Field(default=None)

    # Execution metadata
    bytes_scanned: float = Field(nullable=False)
    duration_ms: int = Field(nullable=False)
    row_count: Optional[int] = Field(default=None)

    # BigQuery job info
    job_id: Optional[str] = Field(default=None, max_length=255)
    cache_hit: bool = Field(default=False, nullable=False)

    # Context
    endpoint: Optional[str] = Field(default=None, max_length=255)
    purpose: QueryPurpose = Field(nullable=False)

    # Timestamps
    executed_at: datetime = Field(default_factory=datetime.utcnow, nullable=False, index=True)

    # Relationships
    dashboard: Optional[Dashboard] = Relationship(back_populates="query_logs")
    user: Optional[User] = Relationship(back_populates="query_logs")

    __table_args__ = (
        Index("idx_query_log_dashboard", "dashboard_id"),
        Index("idx_query_log_executed", "executed_at"),
        Index("idx_query_log_hash_executed", "query_hash", "executed_at"),
    )

    @property
    def estimated_cost_usd(self) -> float:
        """Estimate cost in USD ($5 per TB scanned)."""
        bytes_per_tb = 1024 ** 4
        cost_per_tb = 5.0
        return (self.bytes_scanned / bytes_per_tb) * cost_per_tb
