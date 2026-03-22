import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from studies_api.app import app
from studies_api.core.database import get_connection
from studies_api.core.security import get_password_hash, create_access_token
from studies_api.models.base import Base
from studies_api.models.users import User
from studies_api.models.sessions import Session


@pytest_asyncio.fixture
async def session():
    engine = create_async_engine(
        url='sqlite+aiosqlite:///:memory:',
        echo=False,
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
    await engine.dispose()


@pytest.fixture
def client(session):
    def get_connection_override():
        return session

    with TestClient(app) as client:
        app.dependency_overrides[get_connection] = get_connection_override
        yield client

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def user_data():
    return {
        'username': 'test_user',
        'password': 'secret123',
        'email': 'test@example.com',
    }


@pytest_asyncio.fixture
async def user(session, user_data):
    hashed_password = get_password_hash(user_data['password'])
    db_user = User(
        username=user_data['username'],
        email=user_data['email'],
        password=hashed_password,
    )

    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)

    return db_user


@pytest_asyncio.fixture
async def token(user):
    return create_access_token(data={'sub': str(user.id)})


@pytest_asyncio.fixture
async def authenticated_client(client, token):
    client.headers['Authorization'] = f'Bearer {token}'
    yield client
    client.headers.clear()


@pytest_asyncio.fixture
async def session_data():
    return {
        'topic': 'Python Async',
        'duration_minutes': 60,
        'notes': 'Estudando asyncio e async/await',
        'date': '2026-03-22',
    }


@pytest_asyncio.fixture
async def study_session(authenticated_client, session, session_data, user):
    db_session = Session(
        topic=session_data['topic'],
        duration_minutes=session_data['duration_minutes'],
        notes=session_data['notes'],
        date=session_data['date'],
        user_id=user.id,
    )

    session.add(db_session)
    await session.commit()
    await session.refresh(db_session)

    return db_session
