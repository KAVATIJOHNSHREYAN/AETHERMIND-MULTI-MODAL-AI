import pytest
import asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.database.session import init_db

@pytest.fixture(scope="session", autouse=True)
def initialize_test_database():
    """Ensure database tables are initialized before running tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    loop.run_until_complete(init_db())
    loop.close()

@pytest.fixture
async def async_client():
    """Async HTTP Client fixture for testing FastAPI route endpoints"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        yield client
