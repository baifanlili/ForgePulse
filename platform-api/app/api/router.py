from fastapi import APIRouter

from app.api.routers import alarms, analytics, dashboard, devices, edge, health, system

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(dashboard.router, prefix="/api", tags=["dashboard"])
api_router.include_router(devices.router, prefix="/api/devices", tags=["devices"])
api_router.include_router(alarms.router, prefix="/api/alarms", tags=["alarms"])
api_router.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])
api_router.include_router(system.router, prefix="/api/system", tags=["system"])
api_router.include_router(edge.router, prefix="/api/edge", tags=["edge"])
