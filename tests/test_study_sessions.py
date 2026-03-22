from http import HTTPStatus

import pytest

from studies_api.models.sessions import Session


class TestCreateSession:
    """Testes para criação de sessão de estudo."""

    def test_create_session_success(self, authenticated_client, session_data):
        response = authenticated_client.post('/api/v1/sessions/session', json=session_data)

        assert response.status_code == HTTPStatus.CREATED
        data = response.json()
        assert data['topic'] == session_data['topic']
        assert data['duration_minutes'] == session_data['duration_minutes']
        assert data['notes'] == session_data['notes']
        assert data['date'] == session_data['date']
        assert 'id' in data
        assert 'user_id' in data

    def test_create_session_without_auth(self, client, session_data):
        response = client.post('/api/v1/sessions/session', json=session_data)

        assert response.status_code == HTTPStatus.UNAUTHORIZED

    def test_create_session_invalid_token(self, client, session_data):
        client.headers['Authorization'] = 'Bearer invalid_token'
        response = client.post('/api/v1/sessions/session', json=session_data)

        assert response.status_code == HTTPStatus.UNAUTHORIZED

    def test_create_session_with_empty_notes(self, authenticated_client):
        session_data = {
            'topic': 'Test Topic',
            'duration_minutes': 30,
            'notes': '',
            'date': '2026-03-22',
        }
        response = authenticated_client.post('/api/v1/sessions/session', json=session_data)

        assert response.status_code == HTTPStatus.CREATED


class TestListSessions:
    """Testes para listagem de sessões de estudo."""

    def test_list_sessions_success(self, authenticated_client, study_session):
        response = authenticated_client.get('/api/v1/sessions/sessions')

        assert response.status_code == HTTPStatus.OK
        data = response.json()
        assert 'sessions' in data
        assert 'offset' in data
        assert 'limit' in data
        assert len(data['sessions']) == 1
        assert data['sessions'][0]['topic'] == study_session.topic

    def test_list_sessions_empty(self, authenticated_client):
        response = authenticated_client.get('/api/v1/sessions/sessions')

        assert response.status_code == HTTPStatus.OK
        data = response.json()
        assert data['sessions'] == []
        assert data['offset'] == 0
        assert data['limit'] == 100

    def test_list_sessions_with_pagination(self, authenticated_client, study_session):
        response = authenticated_client.get('/api/v1/sessions/sessions?offset=0&limit=5')

        assert response.status_code == HTTPStatus.OK
        data = response.json()
        assert data['offset'] == 0
        assert data['limit'] == 5

    def test_list_sessions_with_search(self, authenticated_client, study_session):
        response = authenticated_client.get('/api/v1/sessions/sessions?search=Python')

        assert response.status_code == HTTPStatus.OK
        data = response.json()
        assert len(data['sessions']) == 1
        assert data['sessions'][0]['topic'] == 'Python Async'

    def test_list_sessions_search_no_results(self, authenticated_client, study_session):
        response = authenticated_client.get('/api/v1/sessions/sessions?search=nonexistent')

        assert response.status_code == HTTPStatus.OK
        data = response.json()
        assert data['sessions'] == []

    def test_list_sessions_without_auth(self, client):
        response = client.get('/api/v1/sessions/sessions')

        assert response.status_code == HTTPStatus.UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_list_sessions_user_isolation(self, authenticated_client, user, session, session_data):
        # Cria sessão para o usuário autenticado
        user_session = Session(
            topic='User Session',
            duration_minutes=45,
            notes='Visible',
            date='2026-03-22',
            user_id=user.id,
        )
        session.add(user_session)
        # Cria sessão para outro usuário
        other_user = Session(
            topic='Other User Session',
            duration_minutes=60,
            notes='Not visible',
            date='2026-03-22',
            user_id=999,  # ID diferente
        )
        session.add(other_user)
        await session.commit()

        response = authenticated_client.get('/api/v1/sessions/sessions')

        assert response.status_code == HTTPStatus.OK
        data = response.json()
        # Só deve ver suas próprias sessões
        assert len(data['sessions']) == 1
        assert data['sessions'][0]['topic'] == 'User Session'


class TestGetSession:
    """Testes para busca de sessão por ID."""

    def test_get_session_success(self, authenticated_client, study_session):
        response = authenticated_client.get(f'/api/v1/sessions/sessions/{study_session.id}')

        assert response.status_code == HTTPStatus.OK
        data = response.json()
        assert data['id'] == study_session.id
        assert data['topic'] == study_session.topic
        assert data['user_id'] == study_session.user_id

    def test_get_session_not_found(self, authenticated_client):
        response = authenticated_client.get('/api/v1/sessions/sessions/999')

        assert response.status_code == HTTPStatus.NOT_FOUND
        assert 'Study Session Not Found' in response.json()['detail']

    @pytest.mark.asyncio
    async def test_get_session_without_auth(self, client, user, session):
        # Cria sessão diretamente no banco
        study_session = Session(
            topic='Test Session',
            duration_minutes=30,
            notes='Test notes',
            date='2026-03-22',
            user_id=user.id,
        )
        session.add(study_session)
        await session.commit()
        await session.refresh(study_session)

        response = client.get(f'/api/v1/sessions/sessions/{study_session.id}')

        assert response.status_code == HTTPStatus.UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_get_session_ownership_check(self, authenticated_client, session):
        # Cria sessão de outro usuário
        other_session = Session(
            topic='Other Session',
            duration_minutes=30,
            notes='Not accessible',
            date='2026-03-22',
            user_id=999,
        )
        session.add(other_session)
        await session.commit()

        response = authenticated_client.get(f'/api/v1/sessions/sessions/{other_session.id}')

        assert response.status_code == HTTPStatus.FORBIDDEN
        assert 'Do not have permissions' in response.json()['detail']


class TestUpdateSession:
    """Testes para atualização de sessão de estudo."""

    def test_update_session_success(self, authenticated_client, study_session):
        update_data = {
            'topic': 'Updated Topic',
        }
        response = authenticated_client.put(
            f'/api/v1/sessions/sessions/{study_session.id}', json=update_data
        )

        assert response.status_code == HTTPStatus.OK
        data = response.json()
        assert data['topic'] == 'Updated Topic'

    def test_update_session_duration(self, authenticated_client, study_session):
        update_data = {
            'duration_minutes': 90,
        }
        response = authenticated_client.put(
            f'/api/v1/sessions/sessions/{study_session.id}', json=update_data
        )

        assert response.status_code == HTTPStatus.OK
        data = response.json()
        assert data['duration_minutes'] == 90

    def test_update_session_notes(self, authenticated_client, study_session):
        update_data = {
            'notes': 'Updated notes',
        }
        response = authenticated_client.put(
            f'/api/v1/sessions/sessions/{study_session.id}', json=update_data
        )

        assert response.status_code == HTTPStatus.OK
        data = response.json()
        assert data['notes'] == 'Updated notes'

    def test_update_session_date(self, authenticated_client, study_session):
        update_data = {
            'date': '2026-03-23',
        }
        response = authenticated_client.put(
            f'/api/v1/sessions/sessions/{study_session.id}', json=update_data
        )

        assert response.status_code == HTTPStatus.OK
        data = response.json()
        assert data['date'] == '2026-03-23'

    def test_update_session_not_found(self, authenticated_client):
        update_data = {'topic': 'Updated'}
        response = authenticated_client.put('/api/v1/sessions/sessions/999', json=update_data)

        assert response.status_code == HTTPStatus.NOT_FOUND

    @pytest.mark.asyncio
    async def test_update_session_without_auth(self, client, user, session):
        # Cria sessão diretamente no banco
        study_session = Session(
            topic='Test Session',
            duration_minutes=30,
            notes='Test notes',
            date='2026-03-22',
            user_id=user.id,
        )
        session.add(study_session)
        await session.commit()
        await session.refresh(study_session)

        update_data = {'topic': 'Updated'}
        response = client.put(
            f'/api/v1/sessions/sessions/{study_session.id}', json=update_data
        )

        assert response.status_code == HTTPStatus.UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_update_session_ownership_check(self, authenticated_client, session):
        # Cria sessão de outro usuário
        other_session = Session(
            topic='Other Session',
            duration_minutes=30,
            notes='Not editable',
            date='2026-03-22',
            user_id=999,
        )
        session.add(other_session)
        await session.commit()

        update_data = {'topic': 'Hacked'}
        response = authenticated_client.put(
            f'/api/v1/sessions/sessions/{other_session.id}', json=update_data
        )

        assert response.status_code == HTTPStatus.FORBIDDEN


class TestDeleteSession:
    """Testes para exclusão de sessão de estudo."""

    def test_delete_session_success(self, authenticated_client, study_session, session):
        response = authenticated_client.delete(
            f'/api/v1/sessions/sessions/{study_session.id}'
        )

        assert response.status_code == HTTPStatus.NO_CONTENT

        # Verifica se foi deletado
        import asyncio
        from sqlalchemy import select

        async def check_deleted():
            result = await session.execute(
                select(Session).where(Session.id == study_session.id)
            )
            return result.scalar_one_or_none()

        deleted_session = asyncio.run(check_deleted())
        assert deleted_session is None

    def test_delete_session_not_found(self, authenticated_client):
        response = authenticated_client.delete('/api/v1/sessions/sessions/999')

        assert response.status_code == HTTPStatus.NOT_FOUND

    @pytest.mark.asyncio
    async def test_delete_session_without_auth(self, client, user, session):
        # Cria sessão diretamente no banco
        study_session = Session(
            topic='Test Session',
            duration_minutes=30,
            notes='Test notes',
            date='2026-03-22',
            user_id=user.id,
        )
        session.add(study_session)
        await session.commit()
        await session.refresh(study_session)

        response = client.delete(f'/api/v1/sessions/sessions/{study_session.id}')

        assert response.status_code == HTTPStatus.UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_delete_session_ownership_check(self, authenticated_client, session):
        # Cria sessão de outro usuário
        other_session = Session(
            topic='Other Session',
            duration_minutes=30,
            notes='Not deletable',
            date='2026-03-22',
            user_id=999,
        )
        session.add(other_session)
        await session.commit()

        response = authenticated_client.delete(f'/api/v1/sessions/sessions/{other_session.id}')

        assert response.status_code == HTTPStatus.FORBIDDEN


@pytest.mark.asyncio
async def test_session_schema_validation():
    """Testa validação do schema de sessão."""
    from studies_api.schemas.study_sessions import StudySessionSchema

    # Testa schema válido
    session_data = {
        'topic': 'Test',
        'duration_minutes': 60,
        'notes': 'Notes',
        'date': '2026-03-22',
    }
    schema = StudySessionSchema(**session_data)
    assert schema.topic == 'Test'
    assert schema.duration_minutes == 60

    # Testa com notes None
    session_data_null = {
        'topic': 'Test',
        'duration_minutes': 60,
        'notes': None,
        'date': '2026-03-22',
    }
    schema = StudySessionSchema(**session_data_null)
    assert schema.notes is None
