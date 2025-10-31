#!/usr/bin/env python
"""List all API routes with methods and descriptions."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.main import app


def main() -> None:
    """List all routes in the FastAPI app."""
    print("\nPeter Dashboard API - Routes")
    print("=" * 80)
    print(f"{'Method':<8} {'Path':<50} {'Name':<20}")
    print("-" * 80)

    routes = []
    for route in app.routes:
        if hasattr(route, "methods") and hasattr(route, "path"):
            for method in route.methods:
                if method != "HEAD":  # Skip HEAD methods
                    routes.append(
                        {
                            "method": method,
                            "path": route.path,
                            "name": route.name,
                        }
                    )

    # Sort by path then method
    routes.sort(key=lambda x: (x["path"], x["method"]))

    for route in routes:
        print(f"{route['method']:<8} {route['path']:<50} {route['name']:<20}")

    print("-" * 80)
    print(f"\nTotal routes: {len(routes)}\n")


if __name__ == "__main__":
    main()
