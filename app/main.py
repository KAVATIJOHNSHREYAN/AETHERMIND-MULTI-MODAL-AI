from fastapi import FastAPI, Request
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

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Enterprise Lifespan Lifecycle Manager for Connection Pools"""
    logger.info("Initializing AetherMind Multimodal AI Infrastructure...")
    logger.info(f"Environment: {settings.ENVIRONMENT} | Version: {settings.VERSION}")
    
    # Initialize infrastructure connections
    await redis_manager.connect()
    await qdrant_manager.connect()
    
    yield
    
    # Shutdown infrastructure connections
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

if not os.path.exists(static_dir):
    os.makedirs(static_dir, exist_ok=True)
if not os.path.exists(templates_dir):
    os.makedirs(templates_dir, exist_ok=True)

app.mount("/static", StaticFiles(directory=static_dir), name="static")
templates = Jinja2Templates(directory=templates_dir)

@app.get("/", include_in_schema=False)
async def serve_ui(request: Request):
    """Serve Unified Full Stack Application Root Workspace"""
    return templates.TemplateResponse("index.html", {"request": request})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
