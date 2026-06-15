from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routers import alarms, analytics, auth, dashboard, devices, edge, health, system
from app.core.config import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name, version=settings.app_version)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router)
    app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
    app.include_router(dashboard.router, prefix="/api", tags=["dashboard"])
    app.include_router(devices.router, prefix="/api/devices", tags=["devices"])
    app.include_router(alarms.router, prefix="/api/alarms", tags=["alarms"])
    app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])
    app.include_router(system.router, prefix="/api/system", tags=["system"])
    app.include_router(edge.router, prefix="/api/edge", tags=["edge"])
    return app


app = create_app()
