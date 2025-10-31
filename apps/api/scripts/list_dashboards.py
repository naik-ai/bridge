#!/usr/bin/env python
"""List all dashboards in the database."""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from src.db.database import engine, AsyncSessionLocal
from src.models.db_models import Dashboard


async def list_dashboards() -> None:
    """List all dashboards."""
    print("\n📊 Peter Dashboard - Dashboard List")
    print("=" * 80)

    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(Dashboard).where(Dashboard.is_active == True).order_by(Dashboard.slug)
            )
            dashboards = result.scalars().all()

            if not dashboards:
                print("\nNo dashboards found.")
                print("Run 'make db-seed' to create sample dashboards.\n")
                return

            print(f"\nFound {len(dashboards)} dashboard(s):\n")
            print(f"{'Slug':<25} {'Title':<30} {'Version':<8} {'Updated':<20}")
            print("-" * 80)

            for dash in dashboards:
                updated = dash.updated_at.strftime("%Y-%m-%d %H:%M:%S") if dash.updated_at else "N/A"
                print(f"{dash.slug:<25} {dash.title:<30} {dash.version:<8} {updated:<20}")

            print("-" * 80)
            print()

    finally:
        await engine.dispose()


def main() -> None:
    """Main entry point."""
    asyncio.run(list_dashboards())


if __name__ == "__main__":
    main()
