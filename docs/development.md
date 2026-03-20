# Desenvolvimento

Este guia fornece instruções para desenvolvedores que desejam contribuir ou estender a StudiesAPI.

## Ambiente de Desenvolvimento

### Configuração Inicial

```bash
# 1. Clonar repositório
git clone <URL_DO_REPOSITORIO>
cd studies_api

# 2. Instalar dependências (incluindo dev)
poetry install

# 3. Criar arquivo .env
cp .env.example .env
# Editar .env com configurações de desenvolvimento

# 4. Executar migrações
poetry run alembic upgrade head

# 5. Iniciar servidor em modo desenvolvimento
poetry run task run
```

### Comandos Disponíveis

Via **Taskipy** (configurado no `pyproject.toml`):

```bash
# Lint (verificar código)
poetry run task lint

# Formatar código
poetry run task format

# Iniciar servidor de desenvolvimento
poetry run task run

# Servir documentação
poetry run task docs
```

### Comandos Diretos

```bash
# Ruff check
poetry run ruff check

# Ruff format
poetry run ruff format

# FastAPI dev server
poetry run fastapi dev studies_api/app.py
```

---

## Estrutura de Desenvolvimento

### Adicionar Novo Endpoint

1. **Criar Schema** (se necessário)

```python
# studies_api/schemas/example.py
from pydantic import BaseModel, ConfigDict
from typing import Optional


class ExampleSchema(BaseModel):
    name: str
    description: Optional[str] = None


class ExamplePublicSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str
    description: Optional[str]
```

2. **Criar Model** (se necessário)

```python
# studies_api/models/example.py
from datetime import datetime
from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column

from studies_api.models.base import Base


class Example(Base):
    __tablename__ = 'examples'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    description: Mapped[str] = mapped_column(default=None)
    
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        onupdate=func.now(),
        server_default=func.now(),
    )
```

3. **Criar Router**

```python
# studies_api/routers/examples.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from studies_api.core.database import get_connection
from studies_api.core.security import get_current_user
from studies_api.models.users import User
from studies_api.models.example import Example
from studies_api.schemas.example import ExampleSchema, ExamplePublicSchema

router = APIRouter()


@router.post(
    path='/',
    status_code=status.HTTP_201_CREATED,
    response_model=ExamplePublicSchema,
    summary='Create Example',
)
async def create_example(
    example: ExampleSchema,
    db: AsyncSession = Depends(get_connection),
    current_user: User = Depends(get_current_user),
):
    db_example = Example(
        name=example.name,
        description=example.description,
    )
    
    db.add(db_example)
    await db.commit()
    await db.refresh(db_example)
    
    return db_example
```

4. **Registrar Router no app.py**

```python
# studies_api/app.py
from studies_api.routers import examples

app.include_router(
    router=examples.router,
    prefix='/api/v1/examples',
    tags=['Examples'],
)
```

5. **Criar Migração**

```bash
poetry run alembic revision --autogenerate -m "Add examples table"
poetry run alembic upgrade head
```

---

### Adicionar Novo Campo ao Modelo

1. **Atualizar Model**

```python
# studies_api/models/users.py
class User(Base):
    # ... campos existentes
    phone: Mapped[str] = mapped_column(default=None)  # Novo campo
```

2. **Atualizar Schemas**

```python
# studies_api/schemas/users.py
class UserSchema(BaseModel):
    # ... campos existentes
    phone: Optional[str] = None

class UserPublicSchema(BaseModel):
    # ... campos existentes
    phone: Optional[str]
```

3. **Criar Migração**

```bash
poetry run alembic revision --autogenerate -m "Add phone to users"
poetry run alembic upgrade head
```

---

## Trabalhando com Banco de Dados

### Criar Nova Migração

```bash
# Gerar migração automática baseada nos models
poetry run alembic revision --autogenerate -m "description"

# Aplicar migração
poetry run alembic upgrade head

# Verificar status
poetry run alembic current
```

### Reverter Migração

```bash
# Reverter última migração
poetry run alembic downgrade -1

# Reverter para revisão específica
poetry run alembic downgrade <revision_id>
```

### Resetar Banco de Dados

```bash
# Deletar todas as tabelas e migrar do zero
poetry run alembic downgrade base
poetry run alembic upgrade head
```

---

## Debugging

### Logs do FastAPI

O FastAPI em modo desenvolvimento mostra logs detalhados:

```bash
poetry run fastapi dev studies_api/app.py
```

**Saída:**
```
INFO:     Will watch for changes in these directories: /path/to/studies_api
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
INFO:     127.0.0.1:12345 - "GET /docs HTTP/1.1" 200
```

### Debug com Python

```python
# Adicionar prints para debug (desenvolvimento apenas)
import pdb; pdb.set_trace()

# Ou usar logging
import logging
logging.info(f"User ID: {user_id}")
```

### Debug no VS Code

Configuração `.vscode/launch.json`:

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "FastAPI",
            "type": "debugpy",
            "request": "launch",
            "module": "uvicorn",
            "args": [
                "studies_api.app:app",
                "--reload"
            ],
            "jinja": true,
            "justMyCode": true
        }
    ]
}
```

---

## Testes Locais

### Testar com cURL

```bash
# Health check
curl http://127.0.0.1:8000/health_check

# Criar usuário
curl -X POST "http://127.0.0.1:8000/api/v1/users/" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@email.com",
    "password": "password123"
  }'

# Login
curl -X POST "http://127.0.0.1:8000/api/v1/auth/token" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@email.com",
    "password": "password123"
  }'

# Usar token
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
curl -X GET "http://127.0.0.1:8000/api/v1/sessions/sessions" \
  -H "Authorization: Bearer $TOKEN"
```

### Testar com HTTPie

```bash
# Instalar
poetry add --group dev httpie

# Health check
http GET :8000/health_check

# Criar usuário
http POST :8000/api/v1/users/ username=testuser email=test@email.com password=password123

# Login
http POST :8000/api/v1/auth/token email=test@email.com password=password123
```

### Swagger UI

Acesse http://127.0.0.1:8000/docs para:
- Visualizar todos os endpoints
- Testar requisições interativamente
- Autenticar e testar endpoints protegidos

---

## Code Style

### Formatação Automática

```bash
# Formatar todo o código
poetry run task format

# Ou diretamente
poetry run ruff format studies_api/
```

### Lint

```bash
# Verificar problemas
poetry run task lint

# Ou diretamente
poetry run ruff check studies_api/

# Corrigir automaticamente
poetry run ruff check --fix studies_api/
```

### Pre-commit (Opcional)

Configurar para rodar antes de cada commit:

```bash
# Instalar pre-commit
poetry add --group dev pre-commit

# Criar .pre-commit-config.yaml
# hooks:
#   - repo: local
#     hooks:
#       - id: ruff
#         name: ruff
#         entry: poetry run ruff check
#         language: system
#       - id: ruff-format
#         name: ruff-format
#         entry: poetry run ruff format
#         language: system

# Instalar hook
pre-commit install
```

---

## Git Workflow

### Branches

```bash
# Main branch
main

# Branches de feature
feature/nova-funcionalidade
feature/add-examples

# Branches de fix
fix/correcao-bug
fix/resolve-issue-123
```

### Commits

Seguir **Conventional Commits**:

```bash
# Format
<type>(<scope>): <description>

# Exemplos
feat(sessions): add notes field to study sessions
fix(auth): resolve token expiration validation
docs: update API endpoints documentation
style: format code with ruff
refactor(database): extract connection logic
test: add unit tests for auth router
chore: update dependencies
```

### Pull Request

1. Criar branch da feature
2. Implementar mudanças
3. Rodar lint e format
4. Testar localmente
5. Criar PR para main
6. Code review
7. Merge

---

## Adicionar Dependências

### Produção

```bash
# Adicionar nova dependência
poetry add <pacote>

# Exemplo
poetry add redis
```

### Desenvolvimento

```bash
# Adicionar dependência de dev
poetry add --group dev <pacote>

# Exemplo
poetry add --group dev pytest
```

### Atualizar Dependências

```bash
# Atualizar todas
poetry update

# Atualizar específica
poetry update <pacote>
```

---

## Documentação

### Documentar Código

```python
def create_access_token(data: Dict) -> str:
    """
    Cria um token de acesso JWT.
    
    Args:
        data: Dados a serem codificados no token.
            Deve conter pelo menos o 'sub' (user_id).
    
    Returns:
        Token JWT codificado como string.
    
    Example:
        >>> create_access_token({'sub': '123'})
        'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'
    """
    to_encode = data.copy()
    # ...
```

### Atualizar Documentação MKDocs

```bash
# Editar arquivo em docs/
# Exemplo: docs/api-endpoints.md

# Servir documentação localmente
poetry run task docs

# Acessar http://127.0.0.1:8001
```

---

## Problemas Comuns

### Import Errors

```bash
# Verificar se está no ambiente virtual
poetry shell

# Ou usar poetry run
poetry run python -c "from studies_api.app import app"
```

### Database Locked

```bash
# Matar processos e remover lock
rm *.db
poetry run alembic upgrade head
```

### Port in Use

```bash
# Matar processo na porta 8000
lsof -ti:8000 | xargs kill -9

# Ou usar outra porta
poetry run fastapi dev studies_api/app.py --port 8001
```

### Ruff Errors

```bash
# Ver detalhes do erro
poetry run ruff check --output-format=full

# Corrigir automaticamente
poetry run ruff check --fix
```

---

## Checklist de Desenvolvimento

Antes de提交 código:

- [ ] Código formatado (`poetry run task format`)
- [ ] Lint passando (`poetry run task lint`)
- [ ] Imports organizados
- [ ] Type hints em funções
- [ ] Docstrings em funções públicas
- [ ] Testes manuais realizados
- [ ] Migrações criadas (se aplicável)
- [ ] Documentação atualizada (se aplicável)
- [ ] Commit message no padrão Conventional Commits

---

## Próximos Passos

1. [Testes](testing.md) - Execução de testes automatizados
2. [Deploy](deploy.md) - Instruções de implantação
3. [Contribuição](contributing.md) - Como contribuir
