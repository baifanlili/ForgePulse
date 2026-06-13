from fastapi import APIRouter

from app.api.routers import alarms, analytics, dashboard, devices, health

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(dashboard.router, prefix="/api", tags=["dashboard"])
api_router.include_router(devices.router, prefix="/api/devices", tags=["devices"])
api_router.include_router(alarms.router, prefix="/api/alarms", tags=["alarms"])
api_router.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])
