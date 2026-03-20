# Estrutura do Projeto

Este documento descreve a organização de diretórios e arquivos da StudiesAPI.

## Árvore de Diretórios

```
studies_api/
├── .git/                          # Repositório Git
├── .ruff_cache/                   # Cache do Ruff (ignorado)
├── .vscode/                       # Configurações do VS Code
│   └── settings.json              # Settings do editor
├── docs/                          # Documentação do projeto
│   ├── index.md                   # Home da documentação
│   ├── overview.md                # Visão geral
│   ├── prerequisites.md           # Pré-requisitos
│   ├── installation.md            # Instalação
│   ├── configuration.md           # Configuração
│   ├── guidelines.md              # Guidelines
│   ├── structure.md               # Estrutura (este arquivo)
│   ├── api-endpoints.md           # Endpoints da API
│   ├── data-modeling.md           # Modelagem de dados
│   ├── security.md                # Segurança
│   ├── development.md             # Desenvolvimento
│   ├── testing.md                 # Testes
│   ├── deploy.md                  # Deploy
│   ├── contributing.md            # Contribuição
│   └── release-notes.md           # Release notes
├── migrations/                    # Migrações do Alembic
│   ├── versions/                  # Scripts de migração
│   │   └── <revision_id>_<slug>.py
│   ├── env.py                     # Ambiente do Alembic
│   ├── README                     # README do Alembic
│   └── script.py.mako             # Template de migração
├── studies_api/                   # Código fonte da API
│   ├── __init__.py                # Package init
│   ├── app.py                     # Aplicação FastAPI principal
│   ├── core/                      # Configurações centrais
│   │   ├── __init__.py
│   │   ├── database.py            # Configuração do banco de dados
│   │   ├── security.py            # Funções de segurança e autenticação
│   │   └── settings.py            # Configurações de ambiente
│   ├── models/                    # Modelos SQLAlchemy
│   │   ├── __init__.py
│   │   ├── base.py                # Base declarativa
│   │   ├── users.py               # Modelo User
│   │   └── sessions.py            # Modelo Session
│   ├── routers/                   # Endpoints da API
│   │   ├── __init__.py
│   │   ├── auth.py                # Rotas de autenticação
│   │   ├── users.py               # Rotas de usuários
│   │   ├── study_sessions.py      # Rotas de sessões de estudo
│   │   └── stats.py               # Rotas de estatísticas
│   └── schemas/                   # Schemas Pydantic
│       ├── __init__.py
│       ├── auth.py                # Schemas de autenticação
│       ├── users.py               # Schemas de usuários
│       ├── study_sessions.py      # Schemas de sessões
│       └── stats.py               # Schemas de estatísticas
├── tests/                         # Testes automatizados
│   └── __init__.py
├── .gitignore                     # Git ignore
├── .env                           # Variáveis de ambiente (ignorado)
├── .env.example                   # Exemplo de variáveis de ambiente
├── alembic.ini                    # Configuração do Alembic
├── mkdocs.yml                     # Configuração do MKDocs
├── poetry.lock                    # Lock de dependências
├── pyproject.toml                 # Configuração do Poetry
├── README.md                      # README principal
└── run.sh                         # Script de execução
```

## Descrição dos Diretórios

### `/studies_api` (Root do Código)

Contém todo o código fonte da aplicação.

| Arquivo | Descrição |
|---------|-----------|
| `app.py` | Instância principal da aplicação FastAPI |
| `__init__.py` | Marca o diretório como package Python |

### `/studies_api/core`

Configurações centrais e utilitários da aplicação.

| Arquivo | Descrição | Responsabilidades |
|---------|-----------|-------------------|
| `settings.py` | Configurações de ambiente | Carregar variáveis de ambiente, validação com Pydantic |
| `database.py` | Configuração do banco | Criar engine async, gerenciar conexões |
| `security.py` | Segurança | Hash de senha, JWT, autenticação, autorização |

**Exemplo de uso:**
```python
from studies_api.core.settings import Settings
from studies_api.core.database import get_connection
from studies_api.core.security import get_current_user
```

### `/studies_api/models`

Modelos de dados SQLAlchemy que representam as tabelas do banco.

| Arquivo | Descrição | Modelo |
|---------|-----------|--------|
| `base.py` | Base declarativa | Classe base para todos os modelos |
| `users.py` | Tabela de usuários | `User` |
| `sessions.py` | Tabela de sessões | `Session` |

**Exemplo:**
```python
from studies_api.models.users import User
from studies_api.models.sessions import Session
```

### `/studies_api/schemas`

Schemas Pydantic para validação e serialização de dados.

| Arquivo | Descrição | Schemas |
|---------|-----------|---------|
| `auth.py` | Autenticação | `Token`, `LoginRequest` |
| `users.py` | Usuários | `UserSchema`, `UserPublicSchema`, `UserUpdateSchema`, `UserListPublicSchema` |
| `study_sessions.py` | Sessões | `StudySessionSchema`, `StudySessionPublicSchema`, `StudySessionUpdateSchema`, `StudySessionListPublicSchema` |
| `stats.py` | Estatísticas | `StudySessionsStats` |

**Tipos de Schemas:**
- **Input Schema**: Dados de entrada (ex: `UserSchema`)
- **Public Schema**: Dados de saída (ex: `UserPublicSchema`)
- **Update Schema**: Dados para atualização (ex: `UserUpdateSchema`)
- **List Schema**: Listagem paginada (ex: `UserListPublicSchema`)

### `/studies_api/routers`

Endpoints da API organizados por domínio.

| Arquivo | Prefixo | Tags | Descrição |
|---------|---------|------|-----------|
| `auth.py` | `/api/v1/auth` | Authentication | Login, refresh token |
| `users.py` | `/api/v1/users` | Users | CRUD de usuários |
| `study_sessions.py` | `/api/v1/sessions` | Sessions | CRUD de sessões de estudo |
| `stats.py` | `/api/v1/stats` | Stats | Estatísticas de estudo |

**Exemplo de estrutura de router:**
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

### `/migrations`

Scripts de migração do banco de dados gerenciados pelo Alembic.

| Arquivo/Diretório | Descrição |
|-------------------|-----------|
| `versions/` | Scripts de migração gerados automaticamente |
| `env.py` | Configuração do ambiente de migração |
| `script.py.mako` | Template para novas migrações |
| `README` | Documentação do Alembic |

**Comandos úteis:**
```bash
# Criar nova migração
poetry run alembic revision --autogenerate -m "description"

# Aplicar migrações
poetry run alembic upgrade head

# Reverter migração
poetry run alembic downgrade -1
```

### `/tests`

Testes automatizados da aplicação.

| Arquivo | Descrição |
|---------|-----------|
| `__init__.py` | Package init |
| `test_*.py` | Arquivos de teste (a serem criados) |

### `/docs`

Documentação do projeto em Markdown.

| Arquivo | Descrição |
|---------|-----------|
| `index.md` | Home da documentação |
| `*.md` | Demais arquivos de documentação |

### `/.vscode`

Configurações específicas do VS Code.

| Arquivo | Descrição |
|---------|-----------|
| `settings.json` | Configurações do editor, linter, formatter |

## Arquivos de Configuração

### `pyproject.toml`

Configuração principal do projeto Poetry.

**Seções:**
- `[project]`: Metadados e dependências
- `[build-system]`: Sistema de build
- `[dependency-groups]`: Dependências de desenvolvimento
- `[tool.ruff]`: Configuração do Ruff
- `[tool.taskipy.tasks]`: Tarefas disponíveis

### `alembic.ini`

Configuração do Alembic para migrações.

**Principais configurações:**
- `script_location`: Caminho para scripts de migração
- `sqlalchemy.url`: URL do banco de dados
- `[loggers]`: Configuração de logs

### `mkdocs.yml`

Configuração da documentação MKDocs.

**Configura:**
- Tema (Material)
- Estrutura de navegação
- Plugins e extensões

### `.gitignore`

Arquivos e diretórios ignorados pelo Git.

**Principais entradas:**
- `__pycache__/`
- `.env`
- `*.db`
- `.ruff_cache/`
- `.pytest_cache/`

### `.env.example`

Template para o arquivo de variáveis de ambiente.

**Contém:**
- `DATABASE_URL`
- `JWT_SECRET_KEY`
- `JWT_ALGORITHM`
- `JWT_EXPIRATION_MINUTES`

## Fluxo de Dados

```
┌──────────────────────────────────────────────────────────────┐
│                         Request                              │
└──────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────┐
│  FastAPI App (app.py)                                        │
│  - Recebe request                                            │
│  - Roteia para router apropriado                             │
└──────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────┐
│  Router (routers/*.py)                                       │
│  - Valida schema de entrada (Pydantic)                       │
│  - Aplica dependências (auth, db)                            │
│  - Chama lógica de negócio                                   │
└──────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────┐
│  Core Services (core/*.py)                                   │
│  - Segurança: autenticação, autorização                      │
│  - Database: conexões, sessões                               │
└──────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────┐
│  Models (models/*.py)                                        │
│  - Operações no banco de dados                               │
│  - SQLAlchemy ORM                                            │
└──────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────┐
│  Database (SQLite/PostgreSQL)                                │
│  - Persistência de dados                                     │
└──────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────┐
│  Response                                                    │
│  - Serializa modelo para schema (Pydantic)                   │
│  - Retorna JSON                                              │
└──────────────────────────────────────────────────────────────┘
```

## Convenções de Nomes

### Arquivos

- **Módulos Python**: `snake_case.py` (ex: `study_sessions.py`)
- **Testes**: `test_*.py` (ex: `test_users.py`)
- **Migrações**: `<revision_id>_<slug>.py`
- **Documentação**: `kebab-case.md` (ex: `api-endpoints.md`)

### Classes e Funções

| Tipo | Convenção | Exemplo |
|------|-----------|---------|
| Classes | PascalCase | `User`, `StudySession` |
| Funções | snake_case | `get_current_user`, `create_session` |
| Variáveis | snake_case | `user_id`, `study_sessions` |
| Constantes | UPPER_SNAKE_CASE | `JWT_ALGORITHM` |
| Schemas | PascalCase + Suffix | `UserSchema`, `UserPublicSchema` |

## Dependências entre Módulos

```
app.py
├── routers/auth.py
│   ├── core/security.py
│   ├── core/database.py
│   ├── models/users.py
│   └── schemas/auth.py
├── routers/users.py
│   ├── core/security.py
│   ├── core/database.py
│   ├── models/users.py
│   └── schemas/users.py
├── routers/study_sessions.py
│   ├── core/security.py
│   ├── core/database.py
│   ├── models/sessions.py
│   ├── models/users.py
│   └── schemas/study_sessions.py
└── routers/stats.py
    ├── core/security.py
    ├── core/database.py
    ├── models/sessions.py
    └── schemas/stats.py
```

## Próximos Passos

1. [API Endpoints](api-endpoints.md) - Documentação completa dos endpoints
2. [Modelagem de Dados](data-modeling.md) - Estrutura do banco de dados
3. [Desenvolvimento](development.md) - Guia para desenvolvedores
