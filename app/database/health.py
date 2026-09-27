from sqlalchemy import text
from app.database.session import engine
from app.logging.logger import logger

async def check_database_health() -> dict:
    """Execute ping check against database"""
    if engine is None:
        return {
            "status": "degraded",
            "database": "postgresql",
            "connected": False,
            "message": "Async database driver (asyncpg) not installed in local environment"
        }
    try:
        async with engine.connect() as connection:
            result = await connection.execute(text("SELECT 1"))
            if result.scalar() == 1:
                return {"status": "healthy", "database": "postgresql", "connected": True}
    except Exception as e:
        logger.warning(f"Database connection health check warning: {str(e)}")
        return {
            "status": "degraded",
            "database": "postgresql",
            "connected": False,
            "error": str(e)
        }
    return {"status": "unhealthy", "database": "postgresql", "connected": False}
