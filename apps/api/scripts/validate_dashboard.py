#!/usr/bin/env python
"""Validate a dashboard YAML file."""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.db.database import AsyncSessionLocal
from src.integrations.bigquery_client import get_bigquery_client
from src.services.yaml_validation import YAMLValidationService


async def validate_dashboard(file_path: str) -> None:
    """Validate a dashboard YAML file."""
    yaml_path = Path(file_path)

    if not yaml_path.exists():
        print(f"❌ Error: File not found: {file_path}")
        sys.exit(1)

    print(f"\n📋 Validating dashboard: {yaml_path}")
    print("=" * 60)

    # Read YAML content
    yaml_content = yaml_path.read_text()

    # Get service dependencies
    bigquery_client = get_bigquery_client()

    try:
        async with AsyncSessionLocal() as session:
            validator = YAMLValidationService(session, bigquery_client)
            result = await validator.validate_dashboard_yaml(yaml_content)

            if result.is_valid:
                print("✅ Validation passed!")
                print()
                if result.dashboard_metadata:
                    print("Dashboard details:")
                    print(f"  Slug: {result.dashboard_metadata.get('slug')}")
                    print(f"  Title: {result.dashboard_metadata.get('title')}")
                    print(f"  Owner: {result.dashboard_metadata.get('owner')}")
                    print(f"  Queries: {result.dashboard_metadata.get('query_count', 0)}")
                    print(f"  Charts: {result.dashboard_metadata.get('chart_count', 0)}")
            else:
                print("❌ Validation failed!")
                print()
                print("Errors:")
                for i, error in enumerate(result.errors, 1):
                    print(f"  {i}. {error}")
                sys.exit(1)

    except Exception as e:
        print(f"❌ Validation error: {e}")
        sys.exit(1)

    print()


def main() -> None:
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python validate_dashboard.py <path-to-yaml>")
        print("Example: python validate_dashboard.py dashboards/revenue-dashboard.yaml")
        sys.exit(1)

    file_path = sys.argv[1]
    asyncio.run(validate_dashboard(file_path))


if __name__ == "__main__":
    main()
