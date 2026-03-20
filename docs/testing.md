# Testes

Este documento descreve a estratégia de testes e como executar testes na StudiesAPI.

## Visão Geral

A StudiesAPI atualmente não possui testes automatizados implementados. Esta seção descreve a estrutura recomendada para implementação futura de testes.

## Estrutura de Testes Recomendada

### Diretório de Testes

```
tests/
├── __init__.py
├── conftest.py              # Fixtures e configurações
├── test_auth.py             # Testes de autenticação
├── test_users.py            # Testes de usuários
├── test_study_sessions.py   # Testes de sessões de estudo
├── test_stats.py            # Testes de estatísticas
└── test_security.py         # Testes de segurança
```

### Configuração do Pytest

Adicionar ao `pyproject.toml`:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
python_functions = "test_*"
asyncio_mode = "auto"
```

### Dependências de Teste

```bash
# Instalar dependências de teste
poetry add --group dev pytest pytest-asyncio httpx
```

---

## Fixtures (conftest.py)

### Configuração Base

```python
# tests/conftest.py
import asyncio
from typing import AsyncGenerator, Generator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from studies_api.app import app
from studies_api.core.database import get_connection
from studies_api.core.settings import Settings
from studies_api.models.base import Base


# Configurar banco de dados de teste
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test_studies.db"


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Criar event loop para testes async."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def test_engine():
    """Criar engine de teste."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=True)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture(scope="function")
async def test_db(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Criar sessão de banco de dados de teste."""
    async_session = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    async with async_session() as session:
        yield session


@pytest.fixture(scope="function")
async def client(test_db: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Criar cliente HTTP de teste."""
    async def override_get_connection():
        yield test_db
    
    app.dependency_overrides[get_connection] = override_get_connection
    
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest.fixture
async def authenticated_client(client: AsyncClient, test_db: AsyncSession) -> AsyncGenerator[tuple, None]:
    """Criar cliente autenticado."""
    from studies_api.core.security import get_password_hash
    from studies_api.models.users import User
    
    # Criar usuário de teste
    user = User(
        username="testuser",
        email="test@example.com",
        password=get_password_hash("password123"),
    )
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)
    
    # Login para obter token
    response = await client.post(
        "/api/v1/auth/token",
        json={"email": "test@example.com", "password": "password123"},
    )
    token = response.json()["access_token"]
    
    client.headers["Authorization"] = f"Bearer {token}"
    
    yield client, user
    
    client.headers.pop("Authorization")
```

---

## Exemplos de Testes

### Testes de Autenticação

```python
# tests/test_auth.py
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_token_success(client: AsyncClient, test_db: AsyncSession):
    """Testar geração de token com credenciais válidas."""
    from studies_api.core.security import get_password_hash
    from studies_api.models.users import User
    
    # Criar usuário
    user = User(
        username="testuser",
        email="test@example.com",
        password=get_password_hash("password123"),
    )
    test_db.add(user)
    await test_db.commit()
    
    # Tentar login
    response = await client.post(
        "/api/v1/auth/token",
        json={"email": "test@example.com", "password": "password123"},
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_token_invalid_credentials(client: AsyncClient):
    """Testar geração de token com credenciais inválidas."""
    response = await client.post(
        "/api/v1/auth/token",
        json={"email": "invalid@email.com", "password": "wrongpassword"},
    )
    
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"


@pytest.mark.asyncio
async def test_refresh_token(authenticated_client: tuple):
    """Testar refresh de token."""
    client, user = authenticated_client
    
    response = await client.post("/api/v1/auth/refresh_token")
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
```

### Testes de Usuários

```python
# tests/test_users.py
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_user_success(client: AsyncClient):
    """Testar criação de usuário."""
    response = await client.post(
        "/api/v1/users/",
        json={
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "password123",
        },
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "newuser"
    assert data["email"] == "newuser@example.com"
    assert "id" in data
    assert "password" not in data


@pytest.mark.asyncio
async def test_create_user_duplicate_email(client: AsyncClient, test_db: AsyncSession):
    """Testar criação de usuário com email duplicado."""
    from studies_api.core.security import get_password_hash
    from studies_api.models.users import User
    
    user = User(
        username="existinguser",
        email="existing@example.com",
        password=get_password_hash("password123"),
    )
    test_db.add(user)
    await test_db.commit()
    
    response = await client.post(
        "/api/v1/users/",
        json={
            "username": "newuser",
            "email": "existing@example.com",
            "password": "password123",
        },
    )
    
    assert response.status_code == 400
    assert "Email already exists" in response.json()["detail"]


@pytest.mark.asyncio
async def test_list_users(authenticated_client: tuple):
    """Testar listagem de usuários."""
    client, user = authenticated_client
    
    response = await client.get("/api/v1/users/")
    
    assert response.status_code == 200
    data = response.json()
    assert "users" in data
    assert "offset" in data
    assert "limit" in data
```

### Testes de Sessões de Estudo

```python
# tests/test_study_sessions.py
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_session_success(authenticated_client: tuple):
    """Testar criação de sessão de estudo."""
    client, user = authenticated_client
    
    response = await client.post(
        "/api/v1/sessions/session",
        json={
            "topic": "Python",
            "duration_minutes": 60,
            "notes": "Estudo de testes",
            "date": "2026-03-19",
        },
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["topic"] == "Python"
    assert data["duration_minutes"] == 60
    assert data["user_id"] == user.id


@pytest.mark.asyncio
async def test_list_sessions_own_only(authenticated_client: tuple, test_db: AsyncSession):
    """Testar que usuário vê apenas suas sessões."""
    from studies_api.core.security import get_password_hash
    from studies_api.models.sessions import Session
    from studies_api.models.users import User
    
    client, user = authenticated_client
    
    # Criar outro usuário
    other_user = User(
        username="otheruser",
        email="other@example.com",
        password=get_password_hash("password123"),
    )
    test_db.add(other_user)
    
    # Criar sessões para ambos
    session_user = Session(topic="User Topic", duration_minutes=30, date="2026-03-19", user_id=user.id)
    session_other = Session(topic="Other Topic", duration_minutes=30, date="2026-03-19", user_id=other_user.id)
    test_db.add_all([session_user, session_other])
    await test_db.commit()
    
    response = await client.get("/api/v1/sessions/sessions")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["sessions"]) == 1
    assert data["sessions"][0]["topic"] == "User Topic"
```

### Testes de Segurança

```python
# tests/test_security.py
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_protected_endpoint_without_token(client: AsyncClient):
    """Testar endpoint protegido sem token."""
    response = await client.get("/api/v1/sessions/sessions")
    
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_protected_endpoint_with_invalid_token(client: AsyncClient):
    """Testar endpoint protegido com token inválido."""
    client.headers["Authorization"] = "Bearer invalid_token"
    
    response = await client.get("/api/v1/sessions/sessions")
    
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_session_ownership(authenticated_client: tuple, test_db: AsyncSession):
    """Testar validação de ownership de sessão."""
    from studies_api.core.security import get_password_hash
    from studies_api.models.sessions import Session
    from studies_api.models.users import User
    
    client, user = authenticated_client
    
    # Criar outro usuário
    other_user = User(
        username="otheruser",
        email="other@example.com",
        password=get_password_hash("password123"),
    )
    test_db.add(other_user)
    await test_db.commit()
    
    # Criar sessão para outro usuário
    session = Session(
        topic="Other Session",
        duration_minutes=30,
        date="2026-03-19",
        user_id=other_user.id,
    )
    test_db.add(session)
    await test_db.commit()
    
    # Tentar acessar sessão de outro usuário
    response = await client.get(f"/api/v1/sessions/sessions/{session.id}")
    
    assert response.status_code == 403
```

---

## Executar Testes

### Comandos

```bash
# Rodar todos os testes
poetry run pytest

# Rodar com verbose
poetry run pytest -v

# Rodar arquivo específico
poetry run pytest tests/test_auth.py

# Rodar teste específico
poetry run pytest tests/test_auth.py::test_token_success

# Rodar com coverage
poetry run pytest --cov=studies_api --cov-report=html

# Rodar testes marcados
poetry run pytest -m async
```

### Coverage

```bash
# Instalar coverage
poetry add --group dev pytest-cov

# Rodar com coverage
poetry run pytest --cov=studies_api

# Gerar relatório HTML
poetry run pytest --cov=studies_api --cov-report=html

# Abrir relatório
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

---

## CI/CD (GitHub Actions)

### Workflow Exemplo

```yaml
# .github/workflows/tests.yml
name: Tests

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: "3.13"
    
    - name: Install Poetry
      run: |
        curl -sSL https://install.python-poetry.org | python3 -
        export PATH="$HOME/.local/bin:$PATH"
    
    - name: Install dependencies
      run: poetry install
    
    - name: Run lint
      run: poetry run task lint
    
    - name: Run tests
      run: poetry run pytest --cov=studies_api
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
```

---

## Melhores Práticas

### 1. Nomeclatura

```python
def test_<funcionalidade>_<cenário>_<resultado_esperado>():
    pass

# Exemplos
def test_create_user_with_valid_data_returns_201():
    pass

def test_login_with_invalid_credentials_returns_401():
    pass
```

### 2. Arrange-Act-Assert

```python
@pytest.mark.asyncio
async def test_example(client: AsyncClient):
    # Arrange
    data = {"username": "test", "email": "test@email.com", "password": "pass123"}
    
    # Act
    response = await client.post("/api/v1/users/", json=data)
    
    # Assert
    assert response.status_code == 201
```

### 3. Testes Independentes

Cada teste deve:
- Ser independente dos outros
- Criar seus próprios dados
- Limpar após execução
- Não depender de ordem de execução

### 4. Fixtures Reutilizáveis

```python
@pytest.fixture
def user_data():
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "password123",
    }
```

---

## Status Atual

| Tipo de Teste | Status |
|--------------|--------|
| Testes Unitários | ❌ Não implementado |
| Testes de Integração | ❌ Não implementado |
| Testes de Endpoints | ❌ Não implementado |
| Testes de Segurança | ❌ Não implementado |
| Coverage | ❌ Não configurado |
| CI/CD | ❌ Não configurado |

## Roadmap de Testes

- [ ] Configurar pytest e dependências
- [ ] Criar fixtures base (conftest.py)
- [ ] Implementar testes de autenticação
- [ ] Implementar testes de usuários
- [ ] Implementar testes de sessões
- [ ] Implementar testes de stats
- [ ] Configurar coverage
- [ ] Configurar CI/CD
- [ ] Atingir 80%+ de coverage

---

## Próximos Passos

1. [Deploy](deploy.md) - Instruções de implantação
2. [Contribuição](contributing.md) - Como contribuir
3. [Release Notes](release-notes.md) - Histórico de versões
