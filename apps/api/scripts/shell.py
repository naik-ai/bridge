#!/usr/bin/env python
"""Interactive shell with app context for debugging and manual operations."""

import asyncio
import code
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.config import settings
from src.db.database import engine, AsyncSessionLocal
from src.integrations.bigquery_client import get_bigquery_client


def main() -> None:
    """Start interactive shell with app context."""
    SessionLocal = AsyncSessionLocal

    # Setup context
    context = {
        "settings": settings,
        "engine": engine,
        "SessionLocal": SessionLocal,
        "asyncio": asyncio,
        "get_bigquery_client": get_bigquery_client,
    }

    # Import common models and services
    try:
        from src.models.db_models import Dashboard, User, Session, Query

        context.update(
            {
                "Dashboard": Dashboard,
                "User": User,
                "Session": Session,
                "Query": Query,
            }
        )
    except ImportError:
        pass

    # Try to import services
    try:
        from src.services.storage import StorageService
        from src.services.yaml_validation import YAMLValidationService
        from src.services.dashboard_compiler import DashboardCompilerService

        context.update(
            {
                "StorageService": StorageService,
                "YAMLValidationService": YAMLValidationService,
                "DashboardCompilerService": DashboardCompilerService,
            }
        )
    except ImportError:
        pass

    banner = """
    Peter Dashboard - Interactive Shell
    ===================================

    Available objects:
      - settings: Application settings
      - engine: SQLAlchemy async engine
      - SessionLocal: Session factory
      - asyncio: Asyncio module

    Database Models (if available):
      - Dashboard, User, Session, Query

    Services (if available):
      - StorageService, YAMLValidationService, DashboardCompilerService

    Example async usage:
      async def list_dashboards():
          async with SessionLocal() as session:
              result = await session.execute(select(Dashboard))
              return result.scalars().all()

      dashboards = asyncio.run(list_dashboards())
    """

    code.interact(banner=banner, local=context)


if __name__ == "__main__":
    main()
