from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.config.settings import settings
from app.api.router import api_router
from app.logging.logger import logger
import os

# Initialize FastAPI Application
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="AetherMind Multimodal AI - Single Unified Enterprise Multimodal AI Platform",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Router (/api/v1)
app.include_router(api_router, prefix=settings.API_V1_STR)

# Templates & Static Files Setup
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
    """Serve Unified Full Stack Application Root Page"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.on_event("startup")
async def startup_event():
    logger.info("Initializing AetherMind Multimodal AI Platform...")
    logger.info(f"Environment: {settings.ENVIRONMENT} | Debug: {settings.DEBUG}")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down AetherMind Multimodal AI Platform...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
