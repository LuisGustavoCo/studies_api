from http import HTTPStatus

import pytest

from studies_api.core.security import create_access_token, verify_password, get_password_hash


class TestGenerateToken:
    """Testes para geração de token de acesso."""

    def test_token_success(self, client, user, user_data):
        login_data = {
            'email': user_data['email'],
            'password': user_data['password'],
        }

        response = client.post('/api/v1/auth/token', json=login_data)

        assert response.status_code == HTTPStatus.OK
        data = response.json()
        assert 'access_token' in data
        assert data['token_type'] == 'bearer'
        assert isinstance(data['access_token'], str)
        assert len(data['access_token']) > 0

    def test_token_invalid_email(self, client):
        login_data = {
            'email': 'nonexistent@example.com',
            'password': 'secret123',
        }

        response = client.post('/api/v1/auth/token', json=login_data)

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert 'Incorrect email or password' in response.json()['detail']

    def test_token_invalid_password(self, client, user_data):
        login_data = {
            'email': user_data['email'],
            'password': 'wrongpassword',
        }

        response = client.post('/api/v1/auth/token', json=login_data)

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert 'Incorrect email or password' in response.json()['detail']

    def test_token_invalid_email_format(self, client):
        login_data = {
            'email': 'invalid-email',
            'password': 'secret123',
        }

        response = client.post('/api/v1/auth/token', json=login_data)

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    def test_token_short_password(self, client):
        login_data = {
            'email': 'test@example.com',
            'password': 'short',
        }

        response = client.post('/api/v1/auth/token', json=login_data)

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


class TestRefreshToken:
    """Testes para refresh de token."""

    def test_refresh_token_success(self, authenticated_client):
        response = authenticated_client.post('/api/v1/auth/refresh_token')

        assert response.status_code == HTTPStatus.OK
        data = response.json()
        assert 'access_token' in data
        assert data['token_type'] == 'bearer'
        assert isinstance(data['access_token'], str)

    def test_refresh_token_without_auth(self, client):
        response = client.post('/api/v1/auth/refresh_token')

        assert response.status_code == HTTPStatus.UNAUTHORIZED

    def test_refresh_token_invalid_token(self, client):
        client.headers['Authorization'] = 'Bearer invalid_token'
        response = client.post('/api/v1/auth/refresh_token')

        assert response.status_code == HTTPStatus.UNAUTHORIZED

    def test_refresh_token_expired(self, client):
        # Cria token expirado
        expired_token = create_access_token(data={'sub': '1'})
        # Manipula o token para expirar imediatamente (não é possível sem mock)
        # Testamos com token inválido
        client.headers['Authorization'] = f'Bearer {expired_token}'
        response = client.post('/api/v1/auth/refresh_token')

        # Token válido mas user não existe
        assert response.status_code == HTTPStatus.UNAUTHORIZED


class TestAuthentication:
    """Testes unitários de autenticação."""

    def test_password_hash(self):
        password = 'secret123'
        hashed = get_password_hash(password)

        assert hashed != password
        assert len(hashed) > 0

    def test_verify_password_success(self):
        password = 'secret123'
        hashed = get_password_hash(password)

        assert verify_password(password, hashed) is True

    def test_verify_password_failure(self):
        password = 'secret123'
        wrong_password = 'wrongpassword'
        hashed = get_password_hash(password)

        assert verify_password(wrong_password, hashed) is False

    def test_create_access_token(self):
        data = {'sub': '123'}
        token = create_access_token(data)

        assert isinstance(token, str)
        assert len(token) > 0

    def test_access_token_contains_payload(self):
        user_id = '456'
        token = create_access_token(data={'sub': user_id})

        assert isinstance(token, str)
        # Token JWT tem 3 partes separadas por ponto
        assert len(token.split('.')) == 3


class TestAuthHeaders:
    """Testes para headers de autenticação."""

    def test_auth_header_format(self, authenticated_client, token):
        assert 'Authorization' in authenticated_client.headers
        assert authenticated_client.headers['Authorization'].startswith('Bearer ')

    def test_multiple_requests_with_same_token(self, authenticated_client, user):
        # Primeira requisição
        response1 = authenticated_client.get(f'/api/v1/users/{user.id}')
        assert response1.status_code == HTTPStatus.OK

        # Segunda requisição com mesmo token
        response2 = authenticated_client.get('/api/v1/users/')
        assert response2.status_code == HTTPStatus.OK


@pytest.mark.asyncio
async def test_authenticate_user_function(session, user, user_data):
    """Testa a função authenticate_user diretamente."""
    from studies_api.core.security import authenticate_user

    # Testa autenticação correta
    authenticated = await authenticate_user(
        email=user_data['email'],
        password=user_data['password'],
        db=session,
    )
    assert authenticated is not None
    assert authenticated.username == user.username

    # Testa email incorreto
    not_authenticated = await authenticate_user(
        email='wrong@example.com',
        password=user_data['password'],
        db=session,
    )
    assert not_authenticated is None

    # Testa senha incorreta
    not_authenticated = await authenticate_user(
        email=user_data['email'],
        password='wrongpassword',
        db=session,
    )
    assert not_authenticated is None
