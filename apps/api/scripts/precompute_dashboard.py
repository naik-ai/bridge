#!/usr/bin/env python
"""Precompute dashboard data and populate cache."""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.cache import get_cache
from src.db.database import AsyncSessionLocal
from src.integrations.bigquery_client import get_bigquery_client
from src.services.precompute import PrecomputeService


async def precompute_dashboard(slug: str) -> None:
    """Precompute a dashboard."""
    print(f"\n⚡ Precomputing dashboard: {slug}")
    print("=" * 60)

    cache = get_cache()
    bigquery_client = get_bigquery_client()

    try:
        async with AsyncSessionLocal() as session:
            service = PrecomputeService(session, cache, bigquery_client)

            print("Executing queries and populating cache...")
            result = await service.precompute_dashboard(slug)

            print()
            print("✅ Precompute complete!")
            print()
            print("Results:")
            print(f"  Dashboard: {result.slug}")
            print(f"  Queries executed: {result.queries_executed}")
            print(f"  Total bytes scanned: {result.total_bytes_scanned:,}")
            print(f"  Execution time: {result.execution_time_ms:,} ms")
            print(f"  Cache populated: {result.cache_populated}")
            print(f"  Precomputed at: {result.precomputed_at}")
            print()

    except Exception as e:
        print(f"❌ Precompute failed: {e}")
        sys.exit(1)


def main() -> None:
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python precompute_dashboard.py <dashboard-slug>")
        print("Example: python precompute_dashboard.py revenue-dashboard")
        sys.exit(1)

    slug = sys.argv[1]
    asyncio.run(precompute_dashboard(slug))


if __name__ == "__main__":
    main()
