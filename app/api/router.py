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
api_router.include_router(search.router, prefix="/search", tags=["Web Search Integration"])
api_router.include_router(memory.router, prefix="/memory", tags=["Long-Term Memory Engine"])
