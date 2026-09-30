from fastapi import APIRouter
from app.schemas.common import APIResponse
from app.database.health import check_database_health
from app.cache.redis_client import redis_manager
from app.vector.qdrant_client import qdrant_manager
from app.storage.supabase_client import storage_manager
from app.config.settings import settings
import sys
import platform

router = APIRouter()

@router.get("", response_model=APIResponse[dict])
async def health_check():
    """General health status overview"""
    return APIResponse(
        success=True,
        message="AetherMind Multimodal AI Unified Platform Operational",
        data={
            "status": "healthy",
            "version": settings.VERSION,
            "environment": settings.ENVIRONMENT
        }
    )

@router.get("/liveness", response_model=APIResponse[dict])
async def liveness_probe():
    """Liveness Probe"""
    return APIResponse(
        success=True,
        message="Process is alive",
        data={"liveness": True}
    )

@router.get("/readiness", response_model=APIResponse[dict])
async def readiness_probe():
    """Deep Readiness Probe checking all infrastructure connections"""
    db_health = await check_database_health()
    redis_health = await redis_manager.health_check()
    qdrant_health = await qdrant_manager.health_check()
    storage_health = await storage_manager.health_check()

    is_ready = db_health.get("status") in ["healthy", "degraded"]

    return APIResponse(
        success=is_ready,
        message="Infrastructure readiness assessment complete",
        data={
            "ready": is_ready,
            "postgresql": db_health,
            "redis": redis_health,
            "qdrant": qdrant_health,
            "supabase_storage": storage_health,
        }
    )

@router.get("/system", response_model=APIResponse[dict])
async def system_info():
    """Runtime environment and platform metrics"""
    return APIResponse(
        success=True,
        message="System information retrieved",
        data={
            "project": settings.PROJECT_NAME,
            "version": settings.VERSION,
            "python_version": sys.version,
            "platform": platform.platform(),
            "debug_mode": settings.DEBUG,
        }
    )
