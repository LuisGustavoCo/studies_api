# API Endpoints

Documentação completa de todos os endpoints da StudiesAPI.

## Informações Gerais

### URL Base

```
Desenvolvimento: http://127.0.0.1:8000
Produção: <URL_DO_SERVIDOR>
```

### Versionamento

A API utiliza versionamento por URL:

```
/api/v1/<recurso>
```

### Autenticação

A maioria dos endpoints requer autenticação via **JWT Bearer Token**.

**Formato do Header:**
```
Authorization: Bearer <seu_token>
```

### Endpoints Públicos

| Método | Endpoint | Descrição | Auth |
|--------|----------|-----------|------|
| `GET` | `/health_check` | Health check | ❌ |
| `POST` | `/api/v1/auth/token` | Gerar token de acesso | ❌ |
| `POST` | `/api/v1/users/` | Criar usuário | ❌ |

### Endpoints Privados

| Método | Endpoint | Descrição | Auth |
|--------|----------|-----------|------|
| `POST` | `/api/v1/auth/refresh_token` | Refresh de token | ✅ |
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

---

## Health Check

### `GET /health_check`

Verifica se a API está em execução.

**Autenticação:** Não requer

**Response:**
```json
{
  "status": "OK"
}
```

**Status Codes:**
- `200 OK` - API funcionando

---

## Autenticação

### `POST /api/v1/auth/token`

Gera um token de acesso JWT mediante credenciais válidas.

**Autenticação:** Não requer

**Request Body:**
```json
{
  "email": "usuario@email.com",
  "password": "senha123"
}
```

**Schema:**
```python
class LoginRequest(BaseModel):
    email: EmailStr
    password: str  # Mínimo 8 caracteres
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Status Codes:**
- `200 OK` - Token gerado com sucesso
- `401 Unauthorized` - Email ou senha incorretos

**Exemplo cURL:**
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/auth/token" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "usuario@email.com",
    "password": "senha123"
  }'
```

---

### `POST /api/v1/auth/refresh_token`

Atualiza o token de acesso usando um token válido.

**Autenticação:** Requer Bearer Token

**Request Body:** Nenhum

**Response (200 OK):**
```json
{
  "access_token": "novo_eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Status Codes:**
- `200 OK` - Token atualizado
- `401 Unauthorized` - Token inválido ou expirado

**Exemplo cURL:**
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/auth/refresh_token" \
  -H "Authorization: Bearer <seu_token>"
```

---

## Usuários

### `POST /api/v1/users/`

Cria um novo usuário.

**Autenticação:** Não requer

**Request Body:**
```json
{
  "username": "joaosilva",
  "email": "joao@email.com",
  "password": "senha123"
}
```

**Schema:**
```python
class UserSchema(BaseModel):
    username: str  # Mínimo 6 caracteres
    email: EmailStr
    password: str  # Mínimo 8 caracteres
```

**Response (201 Created):**
```json
{
  "id": 1,
  "username": "joaosilva",
  "email": "joao@email.com",
  "created_at": "2026-03-19T10:30:00",
  "updated_at": "2026-03-19T10:30:00"
}
```

**Status Codes:**
- `201 Created` - Usuário criado
- `400 Bad Request` - Username ou email já existem
- `422 Unprocessable Entity` - Validação falhou

**Exemplo cURL:**
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/users/" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "joaosilva",
    "email": "joao@email.com",
    "password": "senha123"
  }'
```

---

### `GET /api/v1/users/`

Lista usuários com paginação e busca.

**Autenticação:** Requer Bearer Token

**Query Parameters:**

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `offset` | int | 0 | Número de registros para pular (mín: 0) |
| `limit` | int | 100 | Limite de registros (1-100) |
| `search` | string | null | Busca por username ou email |

**Response (200 OK):**
```json
{
  "users": [
    {
      "id": 1,
      "username": "joaosilva",
      "email": "joao@email.com",
      "created_at": "2026-03-19T10:30:00",
      "updated_at": "2026-03-19T10:30:00"
    }
  ],
  "offset": 0,
  "limit": 100
}
```

**Exemplo cURL:**
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/users/?offset=0&limit=10&search=joao" \
  -H "Authorization: Bearer <seu_token>"
```

---

### `GET /api/v1/users/{user_id}`

Busca um usuário específico por ID.

**Autenticação:** Requer Bearer Token

**Path Parameters:**

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `user_id` | int | ID do usuário |

**Response (200 OK):**
```json
{
  "id": 1,
  "username": "joaosilva",
  "email": "joao@email.com",
  "created_at": "2026-03-19T10:30:00",
  "updated_at": "2026-03-19T10:30:00"
}
```

**Status Codes:**
- `200 OK` - Usuário encontrado
- `404 Not Found` - Usuário não encontrado

**Exemplo cURL:**
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/users/1" \
  -H "Authorization: Bearer <seu_token>"
```

---

### `PUT /api/v1/users/{user_id}`

Atualiza dados de um usuário.

**Autenticação:** Requer Bearer Token

**Path Parameters:**

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `user_id` | int | ID do usuário |

**Request Body (todos opcionais):**
```json
{
  "username": "novo_username",
  "email": "novo@email.com",
  "password": "nova_senha"
}
```

**Schema:**
```python
class UserUpdateSchema(BaseModel):
    username: Optional[str] = None  # Mínimo 6 caracteres
    email: Optional[EmailStr] = None
    password: Optional[str] = None  # Mínimo 8 caracteres
```

**Response (201 Created):**
```json
{
  "id": 1,
  "username": "novo_username",
  "email": "novo@email.com",
  "created_at": "2026-03-19T10:30:00",
  "updated_at": "2026-03-19T11:00:00"
}
```

**Status Codes:**
- `201 Created` - Usuário atualizado
- `400 Bad Request` - Username ou email já existem
- `404 Not Found` - Usuário não encontrado

**Exemplo cURL:**
```bash
curl -X PUT "http://127.0.0.1:8000/api/v1/users/1" \
  -H "Authorization: Bearer <seu_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "novo_username"
  }'
```

---

### `DELETE /api/v1/users/{user_id}`

Deleta um usuário.

**Autenticação:** Requer Bearer Token

**Path Parameters:**

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `user_id` | int | ID do usuário |

**Response (204 No Content):** Sem corpo

**Status Codes:**
- `204 No Content` - Usuário deletado
- `404 Not Found` - Usuário não encontrado

**Exemplo cURL:**
```bash
curl -X DELETE "http://127.0.0.1:8000/api/v1/users/1" \
  -H "Authorization: Bearer <seu_token>"
```

---

## Sessões de Estudo

### `POST /api/v1/sessions/session`

Cria uma nova sessão de estudo.

**Autenticação:** Requer Bearer Token

**Request Body:**
```json
{
  "topic": "Python Avançado",
  "duration_minutes": 90,
  "notes": "Estudo de async/await e decorators",
  "date": "2026-03-19"
}
```

**Schema:**
```python
class StudySessionSchema(BaseModel):
    topic: str
    duration_minutes: int
    notes: Optional[str]  # Máximo 120 caracteres
    date: str  # Formato: YYYY-MM-DD
```

**Response (201 Created):**
```json
{
  "id": 1,
  "topic": "Python Avançado",
  "duration_minutes": 90,
  "notes": "Estudo de async/await e decorators",
  "date": "2026-03-19",
  "user_id": 1
}
```

**Status Codes:**
- `201 Created` - Sessão criada
- `401 Unauthorized` - Não autenticado
- `422 Unprocessable Entity` - Validação falhou

**Exemplo cURL:**
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/sessions/session" \
  -H "Authorization: Bearer <seu_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Python Avançado",
    "duration_minutes": 90,
    "notes": "Estudo de async/await",
    "date": "2026-03-19"
  }'
```

---

### `GET /api/v1/sessions/sessions`

Lista todas as sessões de estudo do usuário autenticado.

**Autenticação:** Requer Bearer Token

**Query Parameters:**

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `offset` | int | 0 | Número de registros para pular |
| `limit` | int | 100 | Limite de registros (1-100) |
| `search` | string | null | Busca por tópico |

**Response (200 OK):**
```json
{
  "sessions": [
    {
      "id": 1,
      "topic": "Python Avançado",
      "duration_minutes": 90,
      "notes": "Estudo de async/await",
      "date": "2026-03-19",
      "user_id": 1
    }
  ],
  "offset": 0,
  "limit": 100
}
```

**Status Codes:**
- `200 OK` - Sessões listadas
- `401 Unauthorized` - Não autenticado

**Exemplo cURL:**
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/sessions/sessions?offset=0&limit=10&search=Python" \
  -H "Authorization: Bearer <seu_token>"
```

---

### `GET /api/v1/sessions/sessions/{session_id}`

Busca uma sessão de estudo específica por ID.

**Autenticação:** Requer Bearer Token

**Path Parameters:**

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `session_id` | int | ID da sessão |

**Response (200 OK):**
```json
{
  "id": 1,
  "topic": "Python Avançado",
  "duration_minutes": 90,
  "notes": "Estudo de async/await",
  "date": "2026-03-19",
  "user_id": 1
}
```

**Status Codes:**
- `200 OK` - Sessão encontrada
- `403 Forbidden` - Sessão não pertence ao usuário
- `404 Not Found` - Sessão não encontrada

**Exemplo cURL:**
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/sessions/sessions/1" \
  -H "Authorization: Bearer <seu_token>"
```

---

### `PUT /api/v1/sessions/sessions/{session_id}`

Atualiza uma sessão de estudo.

**Autenticação:** Requer Bearer Token

**Path Parameters:**

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `session_id` | int | ID da sessão |

**Request Body (todos opcionais):**
```json
{
  "topic": "Python Avançado Atualizado",
  "duration_minutes": 120,
  "notes": "Novas anotações",
  "date": "2026-03-20"
}
```

**Schema:**
```python
class StudySessionUpdateSchema(BaseModel):
    topic: Optional[str] = None
    duration_minutes: Optional[int] = None
    notes: Optional[str] = None
    date: Optional[str] = None
```

**Response (200 OK):**
```json
{
  "id": 1,
  "topic": "Python Avançado Atualizado",
  "duration_minutes": 120,
  "notes": "Novas anotações",
  "date": "2026-03-20",
  "user_id": 1
}
```

**Status Codes:**
- `200 OK` - Sessão atualizada
- `403 Forbidden` - Sessão não pertence ao usuário
- `404 Not Found` - Sessão não encontrada

**Exemplo cURL:**
```bash
curl -X PUT "http://127.0.0.1:8000/api/v1/sessions/sessions/1" \
  -H "Authorization: Bearer <seu_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "duration_minutes": 120
  }'
```

---

### `DELETE /api/v1/sessions/sessions/{session_id}`

Deleta uma sessão de estudo.

**Autenticação:** Requer Bearer Token

**Path Parameters:**

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `session_id` | int | ID da sessão |

**Response (204 No Content):** Sem corpo

**Status Codes:**
- `204 No Content` - Sessão deletada
- `403 Forbidden` - Sessão não pertence ao usuário
- `404 Not Found` - Sessão não encontrada

**Exemplo cURL:**
```bash
curl -X DELETE "http://127.0.0.1:8000/api/v1/sessions/sessions/1" \
  -H "Authorization: Bearer <seu_token>"
```

---

## Estatísticas

### `GET /api/v1/stats/`

Retorna estatísticas de estudo do usuário autenticado.

**Autenticação:** Requer Bearer Token

**Response (200 OK):**
```json
{
  "total_sessions": 15,
  "total_minutes": 1350,
  "most_studied_topic": "Python Avançado"
}
```

**Schema:**
```python
class StudySessionsStats(BaseModel):
    total_sessions: int
    total_minutes: int
    most_studied_topic: str | None
```

**Descrição dos Campos:**

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `total_sessions` | int | Total de sessões registradas |
| `total_minutes` | int | Soma total de minutos estudados |
| `most_studied_topic` | string ou null | Tópico mais estudado |

**Status Codes:**
- `200 OK` - Estatísticas retornadas
- `401 Unauthorized` - Não autenticado

**Exemplo cURL:**
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/stats/" \
  -H "Authorization: Bearer <seu_token>"
```

---

## Códigos de Status HTTP

| Código | Significado | Descrição |
|--------|-------------|-----------|
| `200` | OK | Requisição bem-sucedida |
| `201` | Created | Recurso criado com sucesso |
| `204` | No Content | Requisição bem-sucedida, sem conteúdo |
| `400` | Bad Request | Requisição inválida |
| `401` | Unauthorized | Não autenticado |
| `403` | Forbidden | Sem permissão |
| `404` | Not Found | Recurso não encontrado |
| `422` | Unprocessable Entity | Erro de validação |

---

## Documentação Interativa

A API possui documentação interativa disponível em:

- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

Estas interfaces permitem:
- Visualizar todos os endpoints
- Testar requisições diretamente no browser
- Ver schemas de request/response
- Autenticar e testar endpoints protegidos

---

## Próximos Passos

1. [Modelagem de Dados](data-modeling.md) - Estrutura do banco
2. [Segurança](security.md) - Autenticação e autorização
3. [Desenvolvimento](development.md) - Guia de desenvolvimento
