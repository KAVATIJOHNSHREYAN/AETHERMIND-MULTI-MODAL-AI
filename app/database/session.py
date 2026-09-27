import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.config.settings import settings
from app.logging.logger import logger
from app.database.base import Base

# Determine Database URL (Support postgresql+asyncpg with fallback to sqlite+aiosqlite)
db_url = settings.DATABASE_URL
if os.getenv("TESTING", "0") == "1":
    db_url = "sqlite+aiosqlite:///:memory:"

try:
    if "postgresql" in db_url:
        engine = create_async_engine(
            db_url,
            echo=settings.DEBUG,
            pool_pre_ping=True,
            future=True,
        )
    else:
        engine = create_async_engine(
            db_url,
            echo=settings.DEBUG,
            future=True,
        )
except Exception as e:
    logger.warning(f"Failed to initialize engine for {db_url}: {e}. Falling back to local SQLite database.")
    db_url = "sqlite+aiosqlite:///./aethermind.db"
    engine = create_async_engine(db_url, echo=settings.DEBUG, future=True)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

async def init_db():
    """Initialize database tables on application startup"""
    global engine, AsyncSessionLocal
    try:
        # Import models so Base metadata registers all table definitions
        import app.models.user  # noqa: F401
        import app.models.settings  # noqa: F401
        import app.models.auth_metadata  # noqa: F401

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables initialized successfully.")
    except Exception as e:
        logger.warning(f"PostgreSQL connection failed ({e}). Re-initializing with SQLite local storage...")
        fallback_url = "sqlite+aiosqlite:///./aethermind.db"
        engine = create_async_engine(fallback_url, echo=settings.DEBUG, future=True)
        AsyncSessionLocal = async_sessionmaker(
            bind=engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Fallback SQLite database initialized successfully.")

async def get_async_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
