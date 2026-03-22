from http import HTTPStatus

import pytest

from studies_api.models.users import User


class TestCreateUser:
    """Testes para criação de usuário."""

    def test_create_user_success(self, client, user_data):
        response = client.post('/api/v1/users/', json=user_data)

        assert response.status_code == HTTPStatus.CREATED
        data = response.json()
        assert data['username'] == user_data['username']
        assert data['email'] == user_data['email']
        assert 'id' in data
        assert 'password' not in data

    def test_create_user_duplicate_username(self, client, user, user_data):
        response = client.post('/api/v1/users/', json=user_data)

        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert 'Username already exists' in response.json()['detail']

    def test_create_user_duplicate_email(self, client, user, user_data):
        new_user_data = {
            'username': 'different_user',
            'password': user_data['password'],
            'email': user_data['email'],
        }
        response = client.post('/api/v1/users/', json=new_user_data)

        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert 'Email already exists' in response.json()['detail']

    def test_create_user_invalid_email(self, client):
        user_data = {
            'username': 'testuser',
            'password': 'secret123',
            'email': 'invalid-email',
        }
        response = client.post('/api/v1/users/', json=user_data)

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    def test_create_user_short_username(self, client):
        user_data = {
            'username': 'short',
            'password': 'secret123',
            'email': 'test@example.com',
        }
        response = client.post('/api/v1/users/', json=user_data)

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    def test_create_user_short_password(self, client):
        user_data = {
            'username': 'testuser',
            'password': 'short',
            'email': 'test@example.com',
        }
        response = client.post('/api/v1/users/', json=user_data)

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


class TestListUsers:
    """Testes para listagem de usuários."""

    def test_list_users_success(self, client, user):
        response = client.get('/api/v1/users/')

        assert response.status_code == HTTPStatus.OK
        data = response.json()
        assert 'users' in data
        assert 'offset' in data
        assert 'limit' in data
        assert len(data['users']) == 1
        assert data['users'][0]['username'] == user.username

    def test_list_users_empty(self, client):
        response = client.get('/api/v1/users/')

        assert response.status_code == HTTPStatus.OK
        data = response.json()
        assert data['users'] == []
        assert data['offset'] == 0
        assert data['limit'] == 100

    def test_list_users_with_pagination(self, client, user):
        response = client.get('/api/v1/users/?offset=0&limit=5')

        assert response.status_code == HTTPStatus.OK
        data = response.json()
        assert data['offset'] == 0
        assert data['limit'] == 5

    def test_list_users_with_search(self, client, user):
        response = client.get('/api/v1/users/?search=test_user')

        assert response.status_code == HTTPStatus.OK
        data = response.json()
        assert len(data['users']) == 1
        assert data['users'][0]['username'] == 'test_user'

    def test_list_users_search_no_results(self, client, user):
        response = client.get('/api/v1/users/?search=nonexistent')

        assert response.status_code == HTTPStatus.OK
        data = response.json()
        assert data['users'] == []


class TestGetUser:
    """Testes para busca de usuário por ID."""

    def test_get_user_success(self, client, user):
        response = client.get(f'/api/v1/users/{user.id}')

        assert response.status_code == HTTPStatus.OK
        data = response.json()
        assert data['id'] == user.id
        assert data['username'] == user.username
        assert data['email'] == user.email

    def test_get_user_not_found(self, client):
        response = client.get('/api/v1/users/999')

        assert response.status_code == HTTPStatus.NOT_FOUND
        assert 'User Not Found' in response.json()['detail']


class TestUpdateUser:
    """Testes para atualização de usuário."""

    def test_update_user_success(self, authenticated_client, user):
        update_data = {
            'username': 'updated_user',
        }
        response = authenticated_client.put(f'/api/v1/users/{user.id}', json=update_data)

        assert response.status_code == HTTPStatus.OK
        data = response.json()
        assert data['username'] == 'updated_user'

    def test_update_user_email(self, authenticated_client, user):
        update_data = {
            'email': 'newemail@example.com',
        }
        response = authenticated_client.put(f'/api/v1/users/{user.id}', json=update_data)

        assert response.status_code == HTTPStatus.OK
        data = response.json()
        assert data['email'] == 'newemail@example.com'

    def test_update_user_password(self, authenticated_client, user):
        update_data = {
            'password': 'newpassword123',
        }
        response = authenticated_client.put(f'/api/v1/users/{user.id}', json=update_data)

        assert response.status_code == HTTPStatus.OK

    def test_update_user_not_found(self, authenticated_client):
        update_data = {'username': 'updated_user'}
        response = authenticated_client.put('/api/v1/users/999', json=update_data)

        assert response.status_code == HTTPStatus.NOT_FOUND

    def test_update_user_unauthorized(self, client, user):
        update_data = {'username': 'updated_user'}
        response = client.put(f'/api/v1/users/{user.id}', json=update_data)

        assert response.status_code == HTTPStatus.UNAUTHORIZED

    def test_update_user_duplicate_username(self, authenticated_client, user, client):
        # Cria outro usuário
        new_user = {
            'username': 'other_user',
            'password': 'secret123',
            'email': 'other@example.com',
        }
        client.post('/api/v1/users/', json=new_user)

        # Tenta atualizar primeiro usuário com username do segundo
        update_data = {'username': 'other_user'}
        response = authenticated_client.put(f'/api/v1/users/{user.id}', json=update_data)

        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert 'Username already taken' in response.json()['detail']


class TestDeleteUser:
    """Testes para exclusão de usuário."""

    def test_delete_user_success(self, authenticated_client, user, session):
        response = authenticated_client.delete(f'/api/v1/users/{user.id}')

        assert response.status_code == HTTPStatus.NO_CONTENT

        # Verifica se foi deletado
        import asyncio
        from sqlalchemy import select

        async def check_deleted():
            result = await session.execute(select(User).where(User.id == user.id))
            return result.scalar_one_or_none()

        deleted_user = asyncio.run(check_deleted())
        assert deleted_user is None

    def test_delete_user_not_found(self, authenticated_client):
        response = authenticated_client.delete('/api/v1/users/999')

        assert response.status_code == HTTPStatus.NOT_FOUND

    def test_delete_user_unauthorized(self, client, user):
        response = client.delete(f'/api/v1/users/{user.id}')

        assert response.status_code == HTTPStatus.UNAUTHORIZED


@pytest.mark.asyncio
async def test_user_schema_validation():
    """Testa validação do schema do usuário."""
    from studies_api.schemas.users import UserSchema

    # Testa username curto
    with pytest.raises(ValueError):
        UserSchema(username='abc', password='secret123', email='test@example.com')

    # Testa senha curta
    with pytest.raises(ValueError):
        UserSchema(username='testuser', password='123', email='test@example.com')

    # Testa email inválido
    with pytest.raises(ValueError):
        UserSchema(username='testuser', password='secret123', email='invalid')
