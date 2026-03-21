import pytest
from sqlalchemy import select

from studies_api.models.users import User


@pytest.mark.asyncio
async def teste_create_user(session):
    new_user = User(
        username='guguinha',
        password='lgm31050906',
        email='guguinha@gmail.com',
    )
    session.add(new_user)
    await session.commit()  # cadastrei user no banco
    # Busquei o user
    user = await session.scalar(select(User).where(User.email == 'guguinha@gmail.com'))
    # Dados do user
    new_user_data = {
        'id': user.id,
        'username': user.username,
        'password': user.password,
        'email': user.email,
    }
    # Dados que espero receber
    assert new_user_data == {
        'id': 1,
        'username': 'guguinha',
        'password': 'lgm31050906',
        'email': 'guguinha@gmail.com',
    }
