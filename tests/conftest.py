import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from studies_api.app import app
from studies_api.core.database import get_connection
from studies_api.models.base import Base


@pytest_asyncio.fixture
async def session():
    engine = create_async_engine(
        url='sqlite+aiosqlite:///:memory'  # Crio banco de dados em memória
    )
    # Crio todas tabelas do banco
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    # Empresto a sessão
    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session
    # Deleto tudo e encerro banco em memória
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
def client(session):
    def get_connection_override():
        return session

    with TestClient(app) as client:
        app.dependency_overrides[get_connection] = get_connection_override
        yield client

        app.dependency_overrides.clear()
