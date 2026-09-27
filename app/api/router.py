from fastapi import APIRouter
from app.api.v1 import (
    health,
    auth,
    user,
    chat,
    image,
    document,
    upload,
    audio,
    providers,
    settings,
    search,
    memory,
    knowledge,
    workspace,
    projects,
    files_manager,
    dashboard,
)

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["System Health"])
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(user.router, prefix="/user", tags=["User Profile & Management"])
api_router.include_router(chat.router, prefix="/chat", tags=["Chat Engine"])
api_router.include_router(image.router, prefix="/image", tags=["Image & Vision Engine"])
api_router.include_router(document.router, prefix="/document", tags=["Document RAG Engine"])
api_router.include_router(upload.router, prefix="/upload", tags=["File Storage & Upload"])
api_router.include_router(audio.router, prefix="/audio", tags=["Speech & Voice Engine"])
api_router.include_router(providers.router, prefix="/providers", tags=["AI Model Providers"])
api_router.include_router(settings.router, prefix="/settings", tags=["Application Settings"])
api_router.include_router(search.router, prefix="/search", tags=["Hybrid Search Integration"])
api_router.include_router(memory.router, prefix="/memory", tags=["Long-Term Memory Engine"])
api_router.include_router(knowledge.router, prefix="/knowledge", tags=["Knowledge Base & RAG System"])

# Phase 9 Cloud Workspace & Productivity Routers
api_router.include_router(workspace.router, prefix="/workspace", tags=["Cloud Workspace Core"])
api_router.include_router(projects.router, prefix="/projects", tags=["Projects Engine"])
api_router.include_router(files_manager.router, prefix="/files", tags=["File Manager & Storage"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Workspace Dashboard Analytics"])
