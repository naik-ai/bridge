"""
Main v1 API router for Peter Dashboard Platform.
Aggregates all v1 endpoint routers.

PDR Reference: §3 (Architecture Overview - API Service)
"""

from fastapi import APIRouter

from src.api.v1 import auth, dashboards, data, health, lineage, precompute, schema, sql

# Create v1 router
router = APIRouter(prefix="/v1")

# Include all endpoint routers
router.include_router(health.router)
router.include_router(auth.router)
router.include_router(dashboards.router)
router.include_router(sql.router)
router.include_router(data.router)
router.include_router(precompute.router)
router.include_router(lineage.router)
router.include_router(schema.router)
