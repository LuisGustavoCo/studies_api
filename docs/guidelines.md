# Guidelines do Projeto

Este documento estabelece as diretrizes e padrões de desenvolvimento para a StudiesAPI.

## Padrões de Código

### Python Style Guide

O projeto utiliza **Ruff** como linter e formatter, configurado no `pyproject.toml`.

#### Configuração Atual

```toml
[tool.ruff]
line-length = 100
exclude = [
    ".git",
    "__pycache__",
    "migrations",
    # ... outros diretórios
]

[tool.ruff.lint]
preview = true
select = ['I', 'F', 'E', 'W', 'PL', 'PT']
ignore = ['PLR2004', 'PLR0917', 'PLR0913']

[tool.ruff.format]
preview = true
quote-style = 'single'
```

#### Regras Ativas

| Código | Descrição |
|--------|-----------|
| `I` | Ordenação de imports (isort) |
| `F` | Erros do Pyflakes |
| `E` | Erros do Pycodestyle |
| `W` | Warnings do Pycodestyle |
| `PL` | Pylint |
| `PT` | Boas práticas para testes |

### Formatação

#### Aspas

Use **aspas simples** para strings:

```python
# ✅ Correto
name = 'John'
message = 'Hello, World!'

# ❌ Incorreto
name = "John"
message = "Hello, World!"
```

#### Comprimento da Linha

Máximo de **100 caracteres** por linha:

```python
# ✅ Correto
very_long_variable_name = (
    some_value + another_value + yet_another_value
)

# ❌ Incorreto
very_long_variable_name = some_value + another_value + yet_another_value + extra_value
```

#### Imports

Ordenados automaticamente pelo Ruff (isort):

```python
# Padrão da stdlib
from datetime import datetime
from typing import List, Optional

# Third-party
from fastapi import APIRouter, Depends
from sqlalchemy import select

# First-party
from studies_api.core.database import get_connection
from studies_api.models.users import User
```

### Type Hints

**Sempre** use type hints em funções e variáveis:

```python
# ✅ Correto
from typing import Optional, List

def create_user(
    username: str,
    email: str,
    password: str,
    db: AsyncSession,
) -> User:
    pass

async def get_users(
    offset: int = 0,
    limit: int = 100,
) -> List[User]:
    pass

user_id: Optional[int] = None
```

### Nomenclatura

#### Classes e Modelos

Use **PascalCase**:

```python
# ✅ Correto
class User(Base):
    pass

class StudySessionSchema(BaseModel):
    pass
```

#### Funções e Variáveis

Use **snake_case**:

```python
# ✅ Correto
def get_current_user():
    pass

user_id = 123
study_sessions = []
```

#### Constantes

Use **UPPER_SNAKE_CASE**:

```python
# ✅ Correto
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_MINUTES = 30
```

#### Private/Protected

Use prefixo `_` para membros privados:

```python
def _internal_helper():
    pass

_internal_variable = None
```

## Estrutura de Arquivos

### Organização por Camadas

```
studies_api/
├── core/           # Configurações centrais
├── models/         # Modelos SQLAlchemy
├── schemas/        # Schemas Pydantic
├── routers/        # Endpoints da API
└── app.py          # Aplicação principal
```

### Imports Relativos

Use imports absolutos a partir do root do projeto:

```python
# ✅ Correto
from studies_api.core.database import get_connection
from studies_api.models.users import User

# ❌ Evitar
from ..core.database import get_connection
from .models import User
```

## Documentação

### Docstrings

Use docstrings para funções públicas:

```python
def create_access_token(data: Dict) -> str:
    """
    Cria um token de acesso JWT.

    Args:
        data: Dados a serem codificados no token.

    Returns:
        Token JWT codificado como string.
    """
    to_encode = data.copy()
    # ...
```

### Comments

Use comentários para explicar **porquê**, não **o quê**:

```python
# ✅ Correto - Explica o motivo
# Converte para string porque o JWT espera sub como string
to_encode.update({'sub': str(user_id)})

# ❌ Incorreto - Redundante
# Incrementa i em 1
i += 1
```

## FastAPI Específico

### Definição de Routers

```python
from fastapi import APIRouter, status

router = APIRouter()


@router.post(
    path='/',
    status_code=status.HTTP_201_CREATED,
    response_model=UserPublicSchema,
    summary='Create New User',
)
async def create_user(user: UserSchema, db: AsyncSession = Depends(get_connection)):
    # Implementação
    pass
```

### Status Codes

Use os códigos HTTP apropriados:

```python
from fastapi import status

# Criação: 201
status_code=status.HTTP_201_CREATED

# Sucesso: 200
status_code=status.HTTP_200_OK

# Sem conteúdo: 204
status_code=status.HTTP_204_NO_CONTENT

# Não encontrado: 404
status_code=status.HTTP_404_NOT_FOUND

# Não autorizado: 401
status_code=status.HTTP_401_UNAUTHORIZED

# Bad request: 400
status_code=status.HTTP_400_BAD_REQUEST
```

### Depends

Use `Depends` para injeção de dependências:

```python
from fastapi import Depends

async def get_session(
    session_id: int,
    db: AsyncSession = Depends(get_connection),
    current_user: User = Depends(get_current_user),
):
    pass
```

## Pydantic Schemas

### Configuração de Model

Sempre use `model_config` para schemas que retornam dados do banco:

```python
from pydantic import BaseModel, ConfigDict


class UserPublicSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str
```

### Validações Personalizadas

Use `field_validator` para validações customizadas:

```python
from pydantic import BaseModel, field_validator


class UserSchema(BaseModel):
    username: str
    password: str

    @field_validator('username')
    def username_min_length(cls, v):
        if len(v) < 6:
            raise ValueError('Username must be greater than 6 characters.')
        return v

    @field_validator('password')
    def password_min_length(cls, v):
        if len(v) < 8:
            raise ValueError('Password must have more than 7 characters.')
        return v
```

### Optional Fields

Use `Optional` para campos opcionais:

```python
from typing import Optional


class StudySessionUpdateSchema(BaseModel):
    topic: Optional[str] = None
    duration_minutes: Optional[int] = None
    notes: Optional[str] = None
```

## SQLAlchemy

### Modelos

```python
from datetime import datetime
from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column, relationship


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    email: Mapped[str] = mapped_column(unique=True)

    updated_at: Mapped[datetime] = mapped_column(
        onupdate=func.now(),
        server_default=func.now(),
    )
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    sessions: Mapped[List['Session']] = relationship(back_populates='users')
```

### Queries Assíncronas

```python
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


async def get_user(user_id: int, db: AsyncSession):
    # Buscar por ID
    user = await db.get(User, user_id)

    # Query com select
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    # Listar com paginação
    result = await db.execute(
        select(User)
        .offset(offset)
        .limit(limit)
    )
    users = result.scalars().all()
```

## Tratamento de Erros

### HTTPException

Use `HTTPException` para erros HTTP:

```python
from fastapi import HTTPException, status


@router.get('/users/{user_id}')
async def get_user(user_id: int):
    user = await db.get(User, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User Not Found',
        )

    return user
```

### Headers em Erros

Inclua headers quando apropriado:

```python
raise HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail='Incorrect email or password',
    headers={'WWW-Authenticate': 'Bearer'},
)
```

## Segurança

### Senhas

Nunca armazene senhas em texto puro:

```python
from studies_api.core.security import get_password_hash, verify_password

# Hash ao criar usuário
hashed_password = get_password_hash(plain_password)

# Verificar login
is_valid = verify_password(plain_password, hashed_password)
```

### Validação de Ownership

Valide posse de recursos:

```python
def verify_study_session_ownership(study_session, current_user):
    if study_session.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Do not have permissions to access this study session',
        )
```

## Taskipy Commands

Use os comandos definidos no `pyproject.toml`:

```bash
# Lint
poetry run task lint

# Formatar
poetry run task format

# Rodar aplicação
poetry run task run

# Documentação
poetry run task docs
```

## Git Commit Messages

Siga o padrão **Conventional Commits**:

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

### Tipos

- `feat`: Nova funcionalidade
- `fix`: Correção de bug
- `docs`: Documentação
- `style`: Formatação/linting
- `refactor`: Refatoração
- `test`: Testes
- `chore`: Configuração/manutenção

### Exemplos

```bash
feat(auth): add JWT token refresh endpoint

fix(users): resolve email validation on update

docs: add API endpoints documentation

style: format code with ruff

refactor(database): extract connection logic to separate function

test: add unit tests for auth router

chore: update dependencies
```

## Checklist de Code Review

- [ ] Código formatado com `ruff format`
- [ ] Lint passando com `ruff check`
- [ ] Type hints em todas as funções
- [ ] Docstrings em funções públicas
- [ ] Imports organizados
- [ ] Nomenclatura seguindo padrões
- [ ] Tratamento de erros adequado
- [ ] Validações de segurança implementadas
- [ ] Testes adicionados (quando aplicável)

## Próximos Passos

1. [Estrutura](structure.md) - Organização de diretórios
2. [API Endpoints](api-endpoints.md) - Documentação da API
3. [Desenvolvimento](development.md) - Guia de desenvolvimento
