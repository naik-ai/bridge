#!/usr/bin/env python
"""Seed database with sample data for development."""

import asyncio
import sys
from datetime import datetime
from pathlib import Path
from uuid import uuid4

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from src.db.database import engine, AsyncSessionLocal
from src.models.db_models import Dashboard, User


async def seed_users(session_factory) -> dict[str, User]:
    """Create sample users."""
    async with session_factory() as session:
        # Check if users exist
        result = await session.execute(select(User))
        existing_users = result.scalars().all()

        if existing_users:
            print("✓ Users already exist, skipping...")
            return {user.email: user for user in existing_users}

        users = [
            User(
                id=uuid4(),
                email="admin@company.com",
                name="Admin User",
                picture=None,
                created_at=datetime.utcnow(),
            ),
            User(
                id=uuid4(),
                email="analyst@company.com",
                name="Data Analyst",
                picture=None,
                created_at=datetime.utcnow(),
            ),
        ]

        for user in users:
            session.add(user)

        await session.commit()
        print(f"✓ Created {len(users)} users")

        return {user.email: user for user in users}


async def seed_dashboards(session_factory, users: dict[str, User]) -> None:
    """Create sample dashboard index entries."""
    async with session_factory() as session:
        # Check if dashboards exist
        result = await session.execute(select(Dashboard))
        existing = result.scalars().all()

        if existing:
            print("✓ Dashboards already exist, skipping...")
            return

        admin = users["admin@company.com"]

        dashboards = [
            Dashboard(
                id=uuid4(),
                slug="revenue-dashboard",
                name="Revenue Dashboard",
                description="Monthly revenue metrics and trends",
                owner_id=admin.id,
                storage_path="dashboards/revenue-dashboard.yaml",
                version=1,
                view_type="analytical",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            ),
            Dashboard(
                id=uuid4(),
                slug="ops-kpis",
                name="Operations KPIs",
                description="Key operational metrics",
                owner_id=admin.id,
                storage_path="dashboards/ops-kpis.yaml",
                version=1,
                view_type="analytical",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            ),
        ]

        for dashboard in dashboards:
            session.add(dashboard)

        await session.commit()
        print(f"✓ Created {len(dashboards)} dashboard index entries")


async def create_sample_yaml_files() -> None:
    """Create sample YAML dashboard files."""
    dashboards_dir = Path("dashboards")
    dashboards_dir.mkdir(exist_ok=True)

    # Sample revenue dashboard YAML
    revenue_yaml = """version: 1
kind: dashboard
slug: revenue-dashboard
title: Revenue Dashboard
owner: admin@company.com
view_type: grid

queries:
  - id: monthly_revenue
    warehouse: bigquery
    sql: |
      SELECT
        DATE_TRUNC(order_date, MONTH) as month,
        SUM(amount) as revenue,
        COUNT(DISTINCT order_id) as order_count
      FROM `project.dataset.orders`
      WHERE order_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 12 MONTH)
      GROUP BY month
      ORDER BY month DESC

  - id: top_products
    warehouse: bigquery
    sql: |
      SELECT
        product_name,
        SUM(amount) as revenue
      FROM `project.dataset.orders`
      WHERE order_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 1 MONTH)
      GROUP BY product_name
      ORDER BY revenue DESC
      LIMIT 10

layout:
  - id: total-revenue-kpi
    type: kpi
    chart: null
    query_ref: monthly_revenue
    title: Total Revenue (Last 12 Months)
    config:
      aggregation: sum
      value_field: revenue
      format: currency
    style:
      color: blue
      size: medium
    position:
      row: 0
      col: 0
      width: 4
      height: 2

  - id: revenue-trend
    type: chart
    chart: line
    query_ref: monthly_revenue
    title: Revenue Trend
    config:
      x_axis: month
      y_axis: revenue
      series:
        - name: Revenue
          field: revenue
          color: blue
    style:
      color: blue
      size: large
    position:
      row: 0
      col: 4
      width: 8
      height: 4

  - id: top-products-chart
    type: chart
    chart: bar
    query_ref: top_products
    title: Top Products (Last Month)
    config:
      x_axis: product_name
      y_axis: revenue
      series:
        - name: Revenue
          field: revenue
          color: green
    style:
      color: green
      size: medium
    position:
      row: 4
      col: 0
      width: 12
      height: 4
"""

    revenue_path = dashboards_dir / "revenue-dashboard.yaml"
    if not revenue_path.exists():
        revenue_path.write_text(revenue_yaml)
        print(f"✓ Created {revenue_path}")
    else:
        print(f"✓ {revenue_path} already exists")

    # Sample ops KPIs YAML
    ops_yaml = """version: 1
kind: dashboard
slug: ops-kpis
title: Operations KPIs
owner: admin@company.com
view_type: grid

queries:
  - id: daily_orders
    warehouse: bigquery
    sql: |
      SELECT
        order_date,
        COUNT(*) as order_count,
        AVG(amount) as avg_order_value
      FROM `project.dataset.orders`
      WHERE order_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
      GROUP BY order_date
      ORDER BY order_date DESC

layout:
  - id: order-count-kpi
    type: kpi
    chart: null
    query_ref: daily_orders
    title: Daily Orders (Avg Last 30 Days)
    config:
      aggregation: avg
      value_field: order_count
      format: number
    style:
      color: purple
      size: medium
    position:
      row: 0
      col: 0
      width: 6
      height: 2

  - id: avg-order-value-kpi
    type: kpi
    chart: null
    query_ref: daily_orders
    title: Average Order Value
    config:
      aggregation: avg
      value_field: avg_order_value
      format: currency
    style:
      color: orange
      size: medium
    position:
      row: 0
      col: 6
      width: 6
      height: 2
"""

    ops_path = dashboards_dir / "ops-kpis.yaml"
    if not ops_path.exists():
        ops_path.write_text(ops_yaml)
        print(f"✓ Created {ops_path}")
    else:
        print(f"✓ {ops_path} already exists")


async def main() -> None:
    """Run all seed operations."""
    print("\n🌱 Seeding database...")
    print("=" * 60)

    session_factory = AsyncSessionLocal

    try:
        # Seed users
        users = await seed_users(session_factory)

        # Seed dashboards
        await seed_dashboards(session_factory, users)

        # Create sample YAML files
        await create_sample_yaml_files()

        print("=" * 60)
        print("✅ Seed complete!\n")
        print("Sample users:")
        for email in users:
            print(f"  - {email}")
        print("\nSample dashboards:")
        print("  - revenue-dashboard (dashboards/revenue-dashboard.yaml)")
        print("  - ops-kpis (dashboards/ops-kpis.yaml)")
        print()

    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
