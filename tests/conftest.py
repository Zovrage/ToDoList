import pytest
from httpx import AsyncClient

from app.main import app



# Фикстуры для асинхронного клиента
@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"

@pytest.fixture(scope="function")
async def async_client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
