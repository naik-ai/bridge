"""
Database base imports for Alembic migrations.
Import all models here so Alembic can detect them.
"""

# Import Base first
from src.models.db_models import Base

# Import all models so Alembic can detect them
from src.models.db_models import (
    Dashboard,
    LineageEdge,
    LineageNode,
    QueryLog,
    Session,
    User,
)

__all__ = [
    "Base",
    "User",
    "Session",
    "Dashboard",
    "LineageNode",
    "LineageEdge",
    "QueryLog",
]
