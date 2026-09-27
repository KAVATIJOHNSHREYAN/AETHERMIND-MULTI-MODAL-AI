from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.config.settings import settings
from app.logging.logger import logger

engine = None
AsyncSessionLocal = None

try:
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=settings.DEBUG,
        pool_pre_ping=True,
        future=True,
    )
    AsyncSessionLocal = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )
except Exception as e:
    logger.warning(f"Database engine initialization deferred ({e}). Async DB driver required for active connections.")

async def get_async_db():
    if AsyncSessionLocal is None:
        raise RuntimeError("Async DB session requested but database driver is not installed.")
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
