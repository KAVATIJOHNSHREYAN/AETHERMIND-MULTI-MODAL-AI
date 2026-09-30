from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager
import os

from app.config.settings import settings
from app.api.router import api_router
from app.logging.logger import logger
from app.cache.redis_client import redis_manager
from app.vector.qdrant_client import qdrant_manager
from app.core.exceptions import BaseAppException
from app.middleware.security import SecurityHeadersMiddleware
from app.middleware.error_handler import (
    global_exception_handler,
    app_exception_handler,
    validation_exception_handler,
)

from app.database.session import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Enterprise Lifespan Lifecycle Manager for Connection Pools"""
    logger.info("Initializing AetherMind Multimodal AI Infrastructure...")
    logger.info(f"Environment: {settings.ENVIRONMENT} | Version: {settings.VERSION}")
    
    await init_db()
    await redis_manager.connect()
    await qdrant_manager.connect()
    
    yield
    
    logger.info("Shutting down AetherMind Infrastructure Pools...")
    await redis_manager.disconnect()
    await qdrant_manager.disconnect()

# Initialize FastAPI Application with Lifespan
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="AetherMind Multimodal AI - Single Unified Enterprise Multimodal AI Platform",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# Exception Handlers Registration
app.add_exception_handler(Exception, global_exception_handler)
app.add_exception_handler(BaseAppException, app_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

# Security Middleware & CORS
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Router (/api/v1)
app.include_router(api_router, prefix=settings.API_V1_STR)

# Static & Templates Setup
templates_dir = os.path.join(os.path.dirname(__file__), "templates")
static_dir = os.path.join(os.path.dirname(__file__), "static")

try:
    if not os.path.exists(static_dir):
        os.makedirs(static_dir, exist_ok=True)
    if not os.path.exists(templates_dir):
        os.makedirs(templates_dir, exist_ok=True)
except Exception as dir_err:
    logger.warning(f"Static/templates directory creation skipped: {dir_err}")

from fastapi.responses import FileResponse

app.mount("/static", StaticFiles(directory=static_dir), name="static")
templates = Jinja2Templates(directory=templates_dir)

@app.get("/manifest.json", include_in_schema=False)
async def serve_manifest():
    """Serve Web App Manifest at Root Level for PWA Discovery"""
    manifest_path = os.path.join(static_dir, "manifest.json")
    return FileResponse(manifest_path, media_type="application/manifest+json")

@app.get("/sw.js", include_in_schema=False)
async def serve_sw():
    """Serve Service Worker at Root Scope for Full Domain PWA Interception"""
    sw_path = os.path.join(static_dir, "sw.js")
    return FileResponse(sw_path, media_type="application/javascript", headers={"Service-Worker-Allowed": "/"})

from app.core.dependencies import get_current_user_or_session
from app.database.session import get_async_db
from app.workspace.dashboard_service import dashboard_service
from app.models.user import User
from sqlalchemy.ext.asyncio import AsyncSession

@app.get("/api/workspace/dashboard", include_in_schema=False)
@app.get("/api/dashboard", include_in_schema=False)
@app.get("/api/v1/workspace/dashboard", include_in_schema=False)
async def serve_root_dashboard_alias(
    request: Request,
    current_user: User = Depends(get_current_user_or_session),
    db: AsyncSession = Depends(get_async_db)
):
    """Direct Root Alias Endpoint for Workspace Dashboard Analytics."""
    data = await dashboard_service.get_dashboard_overview(db=db, user_id=current_user.id)
    return {"success": True, "data": data, "message": "Workspace Dashboard loaded"}

@app.get("/login", include_in_schema=False)
@app.get("/auth", include_in_schema=False)
@app.get("/sso-callback", include_in_schema=False)
async def serve_auth(request: Request):
    """Serve Full-Screen Authentication Page"""
    try:
        return templates.TemplateResponse("auth.html", {"request": request})
    except Exception:
        return templates.TemplateResponse(request=request, name="auth.html", context={})

@app.get("/logout", include_in_schema=False)
async def serve_logout(request: Request):
    """Serve Full-Screen Dedicated Logout Page and clear session cookies"""
    try:
        response = templates.TemplateResponse("auth.html", {"request": request, "view": "logout"})
    except Exception:
        response = templates.TemplateResponse(request=request, name="auth.html", context={"view": "logout"})
    response.delete_cookie("aethermind_token")
    response.delete_cookie("aethermind_session")
    return response

@app.get("/", include_in_schema=False)
async def serve_ui(request: Request):
    """Serve Unified Full Stack Application Root Workspace"""
    try:
        return templates.TemplateResponse(request=request, name="index.html", context={})
    except Exception:
        return templates.TemplateResponse("index.html", {"request": request})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
