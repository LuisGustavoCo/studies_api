# Release Notes

Histórico de versões e mudanças da StudiesAPI.

---

## [0.1.0] - 2026-03-19

### Adicionado

#### Autenticação
- ✅ Implementação de autenticação JWT
- ✅ Endpoint de geração de token (`POST /api/v1/auth/token`)
- ✅ Endpoint de refresh de token (`POST /api/v1/auth/refresh_token`)
- ✅ Validação de token com `get_current_user`
- ✅ Expiração de token configurável (30 minutos padrão)

#### Usuários
- ✅ CRUD completo de usuários
- ✅ Endpoint de criação (`POST /api/v1/users/`)
- ✅ Endpoint de listagem com paginação e busca (`GET /api/v1/users/`)
- ✅ Endpoint de busca por ID (`GET /api/v1/users/{id}`)
- ✅ Endpoint de atualização (`PUT /api/v1/users/{id}`)
- ✅ Endpoint de deleção (`DELETE /api/v1/users/{id}`)
- ✅ Validações de username (mínimo 6 caracteres) e senha (mínimo 8 caracteres)
- ✅ Verificação de unicidade de email e username

#### Sessões de Estudo
- ✅ CRUD completo de sessões de estudo
- ✅ Endpoint de criação (`POST /api/v1/sessions/session`)
- ✅ Endpoint de listagem com paginação e busca (`GET /api/v1/sessions/sessions`)
- ✅ Endpoint de busca por ID (`GET /api/v1/sessions/sessions/{id}`)
- ✅ Endpoint de atualização (`PUT /api/v1/sessions/sessions/{id}`)
- ✅ Endpoint de deleção (`DELETE /api/v1/sessions/sessions/{id}`)
- ✅ Validação de ownership (usuário só acessa suas sessões)
- ✅ Campos: topic, duration_minutes, notes, date

#### Estatísticas
- ✅ Endpoint de estatísticas de estudo (`GET /api/v1/stats/`)
- ✅ Métricas: total_sessions, total_minutes, most_studied_topic

#### Segurança
- ✅ Hash de senhas com Argon2 (pwdlib)
- ✅ Validação de ownership de recursos
- ✅ Proteção de endpoints com HTTPBearer
- ✅ Headers WWW-Authenticate em erros 401

#### Banco de Dados
- ✅ Configuração com SQLAlchemy Async
- ✅ Driver aiosqlite para SQLite
- ✅ Models: User, Session
- ✅ Timestamps automáticos (created_at, updated_at)
- ✅ Relacionamentos One-to-Many (User → Sessions)
- ✅ Migrações com Alembic

#### Configuração
- ✅ Pydantic Settings para variáveis de ambiente
- ✅ Suporte a .env file
- ✅ Configurações: DATABASE_URL, JWT_SECRET_KEY, JWT_ALGORITHM, JWT_EXPIRATION_MINUTES

#### Desenvolvimento
- ✅ Ruff para linting e formatação
- ✅ Taskipy para tasks automatizadas
- ✅ Poetry para gerenciamento de dependências
- ✅ Configuração VS Code incluída
- ✅ .gitignore configurado

#### Documentação
- ✅ Swagger UI automática (/docs)
- ✅ ReDoc automática (/redoc)
- ✅ Health check endpoint (/health_check)
- ✅ Documentação MKDocs com Material
- ✅ Tags organizadas por recurso

### Técnico

#### Estrutura do Projeto
```
studies_api/
├── core/
│   ├── database.py      # Configuração do banco
│   ├── security.py      # Autenticação e segurança
│   └── settings.py      # Configurações
├── models/
│   ├── users.py         # Modelo User
│   └── sessions.py      # Modelo Session
├── routers/
│   ├── auth.py          # Rotas de autenticação
│   ├── users.py         # Rotas de usuários
│   ├── study_sessions.py # Rotas de sessões
│   └── stats.py         # Rotas de estatísticas
├── schemas/
│   ├── auth.py          # Schemas de auth
│   ├── users.py         # Schemas de usuários
│   ├── study_sessions.py # Schemas de sessões
│   └── stats.py         # Schemas de stats
└── app.py               # Aplicação principal
```

#### Dependências Principais
- fastapi[standard] >=0.135.1
- pydantic >=2.12.5
- sqlalchemy[asyncio] >=2.0.48
- aiosqlite >=0.22.1
- pydantic-settings >=2.13.1
- alembic >=1.18.4
- pwdlib[argon2] >=0.3.0
- pyjwt >=2.12.1

#### Tasks Disponíveis
```bash
poetry run task lint      # Ruff check
poetry run task format    # Ruff format
poetry run task run       # FastAPI dev server
poetry run task docs      # MKDocs serve
```

### Conhecido

#### Limitações
- ⚠️ Apenas SQLite como banco de dados (suporte a PostgreSQL via configuração)
- ⚠️ Sem testes automatizados implementados
- ⚠️ Sem rate limiting
- ⚠️ Sem refresh token blacklist
- ⚠️ Paginação básica (apenas offset/limit)

#### Melhorias Futuras
- 🔜 Implementar testes unitários e de integração
- 🔜 Adicionar rate limiting
- 🔜 Suporte a múltiplos bancos de dados
- 🔜 Refresh token com blacklist
- 🔜 Exportação de dados (CSV, JSON)
- 🔜 Dashboard de estatísticas avançadas
- 🔜 CI/CD pipeline

---

## Roadmap

### Versão 0.2.0 (Planejada)
- [ ] Implementar testes automatizados
- [ ] Adicionar rate limiting
- [ ] Configurar CI/CD
- [ ] Melhorar documentação de API

### Versão 0.3.0 (Planejada)
- [ ] Suporte a PostgreSQL
- [ ] Refresh token blacklist
- [ ] Exportação de dados
- [ ] Estatísticas avançadas

### Versão 1.0.0 (Futura)
- [ ] API estável
- [ ] Documentação completa
- [ ] Coverage > 80%
- [ ] Produção ready

---

## Convenção de Versionamento

Este projeto segue [Semantic Versioning](https://semver.org/):

- **MAJOR** (1.0.0): Mudanças incompatíveis
- **MINOR** (0.1.0): Novas funcionalidades compatíveis
- **PATCH** (0.0.1): Correções de bugs compatíveis

### Formato

```
[MAJOR.MINOR.PATCH] - YYYY-MM-DD
```

### Tipos de Mudanças

- **Adicionado**: Novas funcionalidades
- **Alterado**: Mudanças em funcionalidades existentes
- **Descontinuado**: Funcionalidades que serão removidas
- **Removido**: Funcionalidades removidas
- **Corrigido**: Correções de bugs
- **Segurança**: Correções de segurança

---

## Autores

- **LuisGustavoCo** - [gustavoocorreia2005@gmail.com](mailto:gustavoocorreia2005@gmail.com)

---

## Licença

Este projeto é de uso pessoal/educacional.

---

## Links

- [Repositório](https://github.com/LuisGustavoCo/studies_api)
- [Issues](https://github.com/LuisGustavoCo/studies_api/issues)
- [Documentação](index.md)
