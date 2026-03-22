# StudiesAPI



**API RESTful para gerenciamento de sessões de estudo e acompanhamento de métricas de aprendizado**

[Documentação](#-documentação) • [Funcionalidades](#-funcionalidades) • [Tecnologias](#-tecnologias) • [Instalação](#-instalação) • [Testes](#-testes)

</div>

---

## 📖 Sobre o Projeto

A **StudiesAPI** é uma aplicação backend moderna desenvolvida com **FastAPI** que permite aos estudantes registrar, organizar e acompanhar suas sessões de estudo. A API fornece endpoints para CRUD completo de usuários e sessões, autenticação segura com JWT, e estatísticas pessoais de estudo.

### 🎯 Objetivos

- **Organização**: Permitir registro estruturado de sessões de estudo
- **Acompanhamento**: Fornecer métricas de tempo e tópicos estudados
- **Segurança**: Garantir isolamento de dados entre usuários
- **Performance**: Operações assíncronas para alto desempenho

---

## ✨ Funcionalidades

### 🔐 Autenticação e Segurança

| Feature | Descrição |
|---------|-----------|
| **JWT Token** | Autenticação stateless com JSON Web Tokens |
| **Refresh Token** | Atualização de token sem necessidade de relogin |
| **Password Hash** | Senhas criptografadas com Argon2 |
| **Ownership Validation** | Usuários acessam apenas seus próprios recursos |

### 👥 Gerenciamento de Usuários

- ✅ Cadastro com validações (username, email, senha)
- ✅ Listagem com paginação e busca
- ✅ Atualização de dados pessoais
- ✅ Exclusão de conta
- ✅ Validação de unicidade (username/email)

### 📚 Sessões de Estudo

- ✅ Registro de sessões com tópico, duração, notas e data
- ✅ Listagem filtrada por usuário
- ✅ Busca por tópico
- ✅ Atualização parcial ou completa
- ✅ Validação de posse (ownership)

### 📊 Estatísticas

- ✅ Total de sessões registradas
- ✅ Tempo total estudado (em minutos)
- ✅ Tópico mais estudado

---

## 🛠️ Tecnologias

### Core

| Tecnologia | Versão | Descrição |
|------------|--------|-----------|
| **Python** | 3.13+ | Linguagem de programação |
| **FastAPI** | 0.135+ | Framework web assíncrono |
| **SQLAlchemy** | 2.0+ | ORM com suporte async |
| **Alembic** | 1.18+ | Gerenciamento de migrações |

### Segurança

| Tecnologia | Versão | Descrição |
|------------|--------|-----------|
| **PyJWT** | 2.12+ | Geração e validação de tokens JWT |
| **pwdlib** | 0.3+ | Hash de senhas com Argon2 |

### Configuração

| Tecnologia | Versão | Descrição |
|------------|--------|-----------|
| **Pydantic Settings** | 2.13+ | Gerenciamento de configurações |
| **python-dotenv** | - | Carregamento de variáveis de ambiente |

### Desenvolvimento

| Tecnologia | Versão | Descrição |
|------------|--------|-----------|
| **Poetry** | 2.0+ | Gerenciador de dependências |
| **Ruff** | 0.15+ | Linter e formatter |
| **pytest** | 9.0+ | Framework de testes |
| **pytest-asyncio** | 1.3+ | Suporte a testes assíncronos |
| **pytest-cov** | 7.0+ | Coverage de testes |

### Documentação

| Tecnologia | Versão | Descrição |
|------------|--------|-----------|
| **MKDocs** | 1.6+ | Gerador de documentação |
| **MKDocs Material** | 9.7+ | Tema para documentação |
| **pymdown-extensions** | 10.21+ | Extensões Markdown |

---

## 📦 Instalação

### Pré-requisitos

- Python 3.13 ou superior
- Poetry 2.0 ou superior
- Git

### Passo a Passo

```bash
# 1. Clone o repositório
git clone https://github.com/LuisGustavoCo/studies_api.git
cd studies_api

# 2. Instale as dependências
poetry install

# 3. Configure as variáveis de ambiente
cp .env.example .env
# Edite .env com suas configurações

# 4. Execute as migrações do banco
poetry run alembic upgrade head

# 5. Inicie o servidor de desenvolvimento
poetry run fastapi dev studies_api/app.py
```

A API estará disponível em `http://127.0.0.1:8000`

### Comandos Disponíveis (Taskipy)

```bash
# Linting
poetry run task lint

# Formatação de código
poetry run task format

# Executar testes
poetry run task test

# Iniciar servidor de desenvolvimento
poetry run task run

# Servir documentação
poetry run task docs
```

---

## 🧪 Testes

A StudiesAPI possui uma suíte de testes abrangente com **97% de coverage**.

### Estrutura de Testes

```
tests/
├── conftest.py           # Fixtures e configurações
├── test_db.py            # Testes de banco de dados
├── test_auth.py          # Testes de autenticação
├── test_users.py         # Testes de CRUD de usuários
├── test_study_sessions.py # Testes de CRUD de sessões
└── test_stats.py         # Testes de estatísticas
```

### Executando Testes

```bash
# Rodar todos os testes com coverage
poetry run task test

# Rodar testes específicos
poetry run pytest tests/test_users.py -v

# Rodar com relatório HTML de coverage
poetry run pytest --cov=studies_api --cov-report=html
# Abra htmlcov/index.html no browser
```

### Fixtures Disponíveis

| Fixture | Descrição |
|---------|-----------|
| `session` | Session do SQLAlchemy em memória |
| `client` | TestClient do FastAPI |
| `user` | Usuário cadastrado no banco |
| `user_data` | Dados do usuário de teste |
| `token` | Token JWT válido |
| `authenticated_client` | Client com header de autenticação |
| `study_session` | Sessão de estudo cadastrada |
| `session_data` | Dados da sessão de teste |

### Cobertura de Testes

| Módulo | Coverage |
|--------|----------|
| `routers/auth.py` | 100% |
| `routers/users.py` | 98% |
| `routers/study_sessions.py` | 100% |
| `routers/stats.py` | 100% |
| `core/security.py` | 93% |
| **Total** | **97%** |

---

## 📚 Documentação

### Documentação Interativa

A API possui documentação Swagger UI e ReDoc integradas:

- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

### Documentação MKDocs

A documentação completa está disponível no diretório `docs/` e pode ser visualizada localmente:

```bash
poetry run task docs
```

Acesse http://127.0.0.1:8001 para visualizar.

#### Estrutura da Documentação

| Arquivo | Descrição |
|---------|-----------|
| `docs/index.md` | Página inicial |
| `docs/overview.md` | Visão geral do projeto |
| `docs/prerequisites.md` | Pré-requisitos |
| `docs/installation.md` | Guia de instalação |
| `docs/configuration.md` | Configuração de ambiente |
| `docs/guidelines.md` | Guidelines e padrões |
| `docs/structure.md` | Estrutura do projeto |
| `docs/api-endpoints.md` | Documentação da API |
| `docs/data-modeling.md` | Modelagem de dados |
| `docs/security.md` | Segurança e autenticação |
| `docs/development.md` | Guia de desenvolvimento |
| `docs/testing.md` | Testes |
| `docs/deploy.md` | Deploy |
| `docs/contributing.md` | Como contribuir |

---

## 🔌 API Endpoints

### Resumo

| Método | Endpoint | Descrição | Auth |
|--------|----------|-----------|------|
| `GET` | `/health_check` | Health check | ❌ |
| `POST` | `/api/v1/auth/token` | Gerar token | ❌ |
| `POST` | `/api/v1/auth/refresh_token` | Refresh token | ✅ |
| `POST` | `/api/v1/users/` | Criar usuário | ❌ |
| `GET` | `/api/v1/users/` | Listar usuários | ✅ |
| `GET` | `/api/v1/users/{id}` | Buscar usuário | ✅ |
| `PUT` | `/api/v1/users/{id}` | Atualizar usuário | ✅ |
| `DELETE` | `/api/v1/users/{id}` | Deletar usuário | ✅ |
| `POST` | `/api/v1/sessions/session` | Criar sessão | ✅ |
| `GET` | `/api/v1/sessions/sessions` | Listar sessões | ✅ |
| `GET` | `/api/v1/sessions/sessions/{id}` | Buscar sessão | ✅ |
| `PUT` | `/api/v1/sessions/sessions/{id}` | Atualizar sessão | ✅ |
| `DELETE` | `/api/v1/sessions/sessions/{id}` | Deletar sessão | ✅ |
| `GET` | `/api/v1/stats/` | Estatísticas | ✅ |

### Exemplo de Uso

```bash
# 1. Criar usuário
curl -X POST "http://127.0.0.1:8000/api/v1/users/" \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "email": "test@email.com", "password": "senha123"}'

# 2. Obter token
curl -X POST "http://127.0.0.1:8000/api/v1/auth/token" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@email.com", "password": "senha123"}'

# 3. Criar sessão (use o token obtido)
curl -X POST "http://127.0.0.1:8000/api/v1/sessions/session" \
  -H "Authorization: Bearer <SEU_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"topic": "Python", "duration_minutes": 60, "notes": "Estudo", "date": "2026-03-22"}'

# 4. Obter estatísticas
curl -X GET "http://127.0.0.1:8000/api/v1/stats/" \
  -H "Authorization: Bearer <SEU_TOKEN>"
```

---

## 🏗️ Estrutura do Projeto

```
studies_api/
├── studies_api/
│   ├── __init__.py
│   ├── app.py                 # Aplicação FastAPI
│   ├── core/
│   │   ├── database.py        # Configuração do banco
│   │   ├── security.py        # Autenticação e JWT
│   │   └── settings.py        # Variáveis de ambiente
│   ├── models/
│   │   ├── base.py            # Base do SQLAlchemy
│   │   ├── users.py           # Modelo User
│   │   └── sessions.py        # Modelo Session
│   ├── schemas/
│   │   ├── users.py           # Schemas Pydantic User
│   │   ├── study_sessions.py  # Schemas Pydantic Session
│   │   ├── auth.py            # Schemas Pydantic Auth
│   │   └── stats.py           # Schemas Pydantic Stats
│   └── routers/
│       ├── auth.py            # Rotas de autenticação
│       ├── users.py           # Rotas de usuários
│       ├── study_sessions.py  # Rotas de sessões
│       └── stats.py           # Rotas de estatísticas
├── tests/
│   ├── conftest.py            # Fixtures pytest
│   ├── test_db.py             # Testes de banco
│   ├── test_auth.py           # Testes de auth
│   ├── test_users.py          # Testes de usuários
│   ├── test_study_sessions.py # Testes de sessões
│   └── test_stats.py          # Testes de stats
├── migrations/                # Migrações Alembic
├── docs/                      # Documentação MKDocs
├── pyproject.toml             # Dependências e config
├── alembic.ini                # Config Alembic
├── mkdocs.yml                 # Config MKDocs
└── README.md                  # Este arquivo
```

---

## 🔒 Segurança

### JWT Configuration

```python
# Configurações no .env
JWT_SECRET_KEY=sua_chave_secreta_aqui
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=30
```

### Validações de Schema

| Campo | Validação |
|-------|-----------|
| `username` | Mínimo 6 caracteres |
| `password` | Mínimo 8 caracteres |
| `email` | Formato EmailStr válido |
| `notes` | Máximo 120 caracteres |

### Ownership

Todos os endpoints de sessões validam que o usuário autenticado é o proprietário do recurso, retornando `403 Forbidden` em caso de violação.

---

## 🚀 Deploy

### Variáveis de Ambiente

```bash
# .env
DATABASE_URL=sqlite+aiosqlite:///./studies.db
JWT_SECRET_KEY=sua_chave_secreta
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=30
```

### Produção

Para deploy em produção, recomenda-se:

1. Usar banco de dados PostgreSQL
2. Configurar variáveis de ambiente seguras
3. Usar servidor ASGI (uvicorn/gunicorn)
4. Configurar HTTPS
5. Implementar rate limiting

```bash
# Exemplo com uvicorn
uvicorn studies_api.app:app --host 0.0.0.0 --port 8000
```

---

## 🤝 Contribuição

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

### Guidelines

- Siga o estilo de código definido pelo Ruff
- Adicione testes para novas funcionalidades
- Mantenha o coverage acima de 80%
- Documente novas features no MKDocs

---

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

## 👤 Autor

**Luis Gustavo**

- GitHub: [@LuisGustavoCo](https://github.com/LuisGustavoCo)
- Email: gustavoocorreia2005@gmail.com

---

## 📊 Status do Projeto

| Métrica | Status |
|---------|--------|
| Testes | ✅ 82 testes passando |
| Coverage | ✅ 97% |
| Documentação | ✅ Completa |
| Type Hints | ✅ 100% |
| Async | ✅ Completo |

---

<div align="center">

**StudiesAPI** &copy; 2026 - Desenvolvido como estudo de FastAPI

[⬆ Voltar ao topo](#studiesapi)

</div>
