import pytest
from sqlalchemy import text, select
from sqlalchemy.ext.asyncio import AsyncSession

from studies_api.models.users import User
from studies_api.models.sessions import Session


@pytest.mark.asyncio
async def test_database_connection(session):
    """Testa se a conexão com o banco de dados está funcionando."""
    result = await session.execute(text('SELECT 1'))
    assert result.scalar() == 1


@pytest.mark.asyncio
async def test_database_tables_created(session):
    """Testa se as tabelas foram criadas corretamente."""
    result = await session.execute(
        text(
            "SELECT name FROM sqlite_master WHERE type='table' AND name IN ('users', 'sessions')"
        )
    )
    tables = result.fetchall()
    assert len(tables) == 2


@pytest.mark.asyncio
async def test_session_is_async_session(session):
    """Testa se a sessão é uma AsyncSession."""
    assert isinstance(session, AsyncSession)


@pytest.mark.asyncio
async def test_can_insert_and_query_user(session):
    """Testa inserção e consulta de usuário no banco em memória."""
    user = User(username='test_db_user', email='testdb@example.com', password='hashed_pwd')
    session.add(user)
    await session.commit()

    result = await session.execute(select(User).where(User.username == 'test_db_user'))
    retrieved_user = result.scalar_one()

    assert retrieved_user is not None
    assert retrieved_user.username == 'test_db_user'
    assert retrieved_user.email == 'testdb@example.com'


@pytest.mark.asyncio
async def test_can_insert_and_query_session(session, user):
    """Testa inserção e consulta de sessão de estudo no banco em memória."""
    study_session = Session(
        topic='Test Topic',
        duration_minutes=30,
        notes='Test notes',
        date='2026-03-22',
        user_id=user.id,
    )
    session.add(study_session)
    await session.commit()

    result = await session.execute(select(Session).where(Session.topic == 'Test Topic'))
    retrieved_session = result.scalar_one()

    assert retrieved_session is not None
    assert retrieved_session.topic == 'Test Topic'
    assert retrieved_session.duration_minutes == 30
    assert retrieved_session.user_id == user.id


@pytest.mark.asyncio
async def test_database_isolation(session):
    """Testa que o banco de dados é isolado para testes."""
    # Conta usuários antes
    result = await session.execute(select(User))
    initial_count = len(result.scalars().all())

    # Adiciona novo usuário
    user = User(username='isolation_test', email='isolation@example.com', password='pwd')
    session.add(user)
    await session.commit()

    # Conta depois
    result = await session.execute(select(User))
    final_count = len(result.scalars().all())

    assert final_count == initial_count + 1


@pytest.mark.asyncio
async def test_user_relationship_with_sessions(session, user):
    """Testa o relacionamento entre User e Session."""
    from sqlalchemy.orm import selectinload

    study_session = Session(
        topic='Relationship Test',
        duration_minutes=45,
        notes='Testing relationships',
        date='2026-03-22',
        user_id=user.id,
    )
    session.add(study_session)
    await session.commit()

    # Busca usuário com sessões usando selectinload para carregamento eager
    result = await session.execute(
        select(User)
        .where(User.id == user.id)
        .options(selectinload(User.sessions))
    )
    retrieved_user = result.scalar_one()

    assert len(retrieved_user.sessions) == 1
    assert retrieved_user.sessions[0].topic == 'Relationship Test'
