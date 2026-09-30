import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.config.settings import settings
from app.logging.logger import logger
from app.database.base import Base

def get_sqlite_url() -> str:
    """Return SQLite database URL."""
    return "sqlite+aiosqlite:///./aethermind.db"

# Determine Database URL (Support postgresql+asyncpg with fallback to sqlite+aiosqlite)
db_url = settings.DATABASE_URL

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
    logger.warning(f"Failed to initialize engine for {db_url}: {e}. Falling back to SQLite database.")
    db_url = get_sqlite_url()
    engine = create_async_engine(db_url, echo=settings.DEBUG, future=True)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

async def init_db():
    """Initialize database tables on application startup safely."""
    global engine, AsyncSessionLocal
    try:
        # Import models so Base metadata registers all table definitions
        import app.models.user  # noqa: F401
        import app.models.settings  # noqa: F401
        import app.models.auth_metadata  # noqa: F401
        import app.models.chat  # noqa: F401
        import app.models.message  # noqa: F401
        import app.models.file  # noqa: F401
        import app.models.memory  # noqa: F401
        import app.models.workspace  # noqa: F401

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            
            # Helper column patcher for SQLite fallback when new model attributes are added
            if engine.dialect.name == "sqlite":
                from sqlalchemy import text
                async_conn = conn
                
                try:
                    result = await async_conn.execute(text("PRAGMA table_info(files)"))
                    file_cols = [row[1] for row in result.fetchall()]
                    
                    file_patch = [
                        ("chat_id", "VARCHAR(36)"),
                        ("folder_id", "VARCHAR(36)"),
                        ("project_id", "VARCHAR(36)"),
                        ("is_starred", "INTEGER DEFAULT 0"),
                        ("is_bookmarked", "INTEGER DEFAULT 0"),
                        ("is_deleted", "INTEGER DEFAULT 0"),
                        ("deleted_at", "DATETIME"),
                        ("tags", "VARCHAR(255)"),
                        ("extracted_text", "TEXT"),
                        ("vector_point_id", "VARCHAR(255)"),
                        ("media_metadata", "TEXT"),
                    ]
                    for col, col_def in file_patch:
                        if col not in file_cols:
                            await async_conn.execute(text(f"ALTER TABLE files ADD COLUMN {col} {col_def}"))
                except Exception as patch_err:
                    logger.warning(f"File table patch notice: {patch_err}")

                try:
                    result = await async_conn.execute(text("PRAGMA table_info(memory_metadata)"))
                    mem_cols = [row[1] for row in result.fetchall()]
                    mem_patch = [
                        ("memory_type", "VARCHAR(50) DEFAULT 'general'"),
                        ("memory_key", "VARCHAR(255)"),
                        ("memory_value", "TEXT"),
                        ("category", "VARCHAR(100) DEFAULT 'general'"),
                        ("importance_score", "FLOAT DEFAULT 0.5"),
                        ("is_pinned", "INTEGER DEFAULT 0"),
                        ("qdrant_vector_id", "VARCHAR(255)"),
                        ("extra_metadata", "TEXT"),
                    ]
                    for col, col_def in mem_patch:
                        if col not in mem_cols:
                            await async_conn.execute(text(f"ALTER TABLE memory_metadata ADD COLUMN {col} {col_def}"))
                except Exception as patch_err:
                    logger.warning(f"Memory table patch notice: {patch_err}")

                try:
                    result = await async_conn.execute(text("PRAGMA table_info(chats)"))
                    chat_cols = [row[1] for row in result.fetchall()]
                    chat_patch = [
                        ("project_id", "VARCHAR(36)"),
                        ("is_starred", "INTEGER DEFAULT 0"),
                        ("is_bookmarked", "INTEGER DEFAULT 0"),
                        ("is_deleted", "INTEGER DEFAULT 0"),
                    ]
                    for col, col_def in chat_patch:
                        if col not in chat_cols:
                            await async_conn.execute(text(f"ALTER TABLE chats ADD COLUMN {col} {col_def}"))
                except Exception as patch_err:
                    logger.warning(f"Chats table patch notice: {patch_err}")

        logger.info("Database tables and columns initialized successfully.")
    except Exception as e:
        logger.warning(f"DB Connection / Init notice ({e}). Re-initializing with SQLite storage...")
        fallback_url = get_sqlite_url()
        try:
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
        except Exception as fb_err:
            logger.error(f"Critical fallback DB init notice: {fb_err}")

async def get_async_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
