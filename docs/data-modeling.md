# Modelagem do Sistema

Este documento descreve a modelagem de dados, arquitetura do sistema e fluxos principais da StudiesAPI.

## Modelos de Dados

### Visão Geral

A API utiliza dois modelos principais para persistência de dados:

- **User**: Representa os usuários do sistema
- **Session**: Representa as sessões de estudo

### Diagrama Entidade-Relacionamento (ERD)

```mermaid
erDiagram
    USER ||--o{ SESSION : "possui"
    
    USER {
        int id PK
        string username UK
        string email UK
        string password
        datetime created_at
        datetime updated_at
    }
    
    SESSION {
        int id PK
        string topic
        int duration_minutes
        string notes
        string date
        int user_id FK
        datetime created_at
        datetime updated_at
    }
```

### Modelo User

**Tabela:** `users`

| Coluna | Tipo | Restrições | Descrição |
|--------|------|------------|-----------|
| `id` | INTEGER | PRIMARY KEY, AUTOINCREMENT | Identificador único |
| `username` | VARCHAR | UNIQUE, NOT NULL | Nome de usuário |
| `email` | VARCHAR | UNIQUE, NOT NULL | Email do usuário |
| `password` | VARCHAR | NOT NULL | Senha (hash Argon2) |
| `created_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP | Data de criação |
| `updated_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP, ON UPDATE | Data de atualização |

**Relacionamentos:**
- One-to-Many com `Session` (um usuário tem várias sessões)

**Validações:**
- Username: mínimo 6 caracteres
- Email: formato válido (EmailStr)
- Password: mínimo 8 caracteres

### Modelo Session

**Tabela:** `sessions`

| Coluna | Tipo | Restrições | Descrição |
|--------|------|------------|-----------|
| `id` | INTEGER | PRIMARY KEY, AUTOINCREMENT | Identificador único |
| `topic` | VARCHAR | NOT NULL | Tópico estudado |
| `duration_minutes` | INTEGER | NOT NULL | Duração em minutos |
| `notes` | TEXT(120) | NULLABLE | Anotações (máx 120 chars) |
| `date` | VARCHAR | NOT NULL | Data da sessão |
| `user_id` | INTEGER | FOREIGN KEY → users.id | ID do usuário |
| `created_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP | Data de criação |
| `updated_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP, ON UPDATE | Data de atualização |

**Relacionamentos:**
- Many-to-One com `User` (várias sessões pertencem a um usuário)

**Validações:**
- Topic: obrigatório
- Duration: inteiro positivo
- Notes: opcional, máximo 120 caracteres
- Date: formato string (YYYY-MM-DD recomendado)

---

## Arquitetura do Sistema

### Arquitetura em Camadas

```mermaid
graph TB
    subgraph "Camada de Apresentação"
        Client[Cliente HTTP<br/>Browser/Mobile/Postman]
        Swagger[Swagger UI / ReDoc]
    end
    
    subgraph "Camada de Aplicação"
        FastAPI[FastAPI Application<br/>app.py]
        Routers[Routers<br/>auth, users, sessions, stats]
    end
    
    subgraph "Camada de Negócio"
        Core[Core Services<br/>security, database, settings]
        Schemas[Schemas Pydantic<br/>Validação e Serialização]
    end
    
    subgraph "Camada de Dados"
        Models[Models SQLAlchemy<br/>User, Session]
        ORM[ORM Layer<br/>SQLAlchemy Async]
    end
    
    subgraph "Persistência"
        DB[(Banco de Dados<br/>SQLite/PostgreSQL)]
    end
    
    Client --> FastAPI
    Swagger --> FastAPI
    FastAPI --> Routers
    Routers --> Core
    Routers --> Schemas
    Routers --> Models
    Models --> ORM
    ORM --> DB
```

### Fluxo de Requisição

```mermaid
sequenceDiagram
    participant C as Cliente
    participant F as FastAPI
    participant R as Router
    participant S as Security/Core
    participant M as Model
    participant D as Database
    
    C->>F: HTTP Request
    F->>R: Roteia para endpoint
    R->>S: Valida autenticação
    S-->>R: Usuário atual ou erro
    R->>S: Valida autorização
    S-->>R: Acesso permitido ou erro
    R->>M: Executa operação
    M->>D: Query SQL
    D-->>M: Resultado
    M-->>R: Modelo/Lista
    R->>S: Serializa resposta
    S-->>R: Schema Pydantic
    R-->>F: Response
    F-->>C: HTTP Response
```

---

## Fluxo de Autenticação

### Diagrama de Autenticação

```mermaid
sequenceDiagram
    participant U as Usuário
    participant A as API (Auth Router)
    participant S as Security Service
    participant DB as Database
    
    U->>A: POST /auth/token<br/>(email, password)
    A->>S: authenticate_user()
    S->>DB: SELECT user WHERE email=?
    DB-->>S: User ou None
    S->>S: verify_password()
    alt Usuário inválido
        S-->>A: None
        A-->>U: 401 Unauthorized
    else Usuário válido
        S-->>A: User
        A->>S: create_access_token(user.id)
        S->>S: JWT.encode(sub=user_id, exp=30min)
        S-->>A: access_token
        A-->>U: 200 OK<br/>{access_token, token_type}
    end
```

### Fluxo de Refresh de Token

```mermaid
sequenceDiagram
    participant U as Usuário
    participant A as API (Auth Router)
    participant S as Security Service
    
    U->>A: POST /auth/refresh_token<br/>(Bearer: token_atual)
    A->>S: get_current_user(token)
    S->>S: verify_token()
    alt Token inválido/expirado
        S-->>A: HTTPException 401
        A-->>U: 401 Unauthorized
    else Token válido
        S->>S: Extrai user_id do sub
        S-->>A: User atual
        A->>S: create_access_token(user.id)
        S-->>A: novo_access_token
        A-->>U: 200 OK<br/>{novo_token, token_type}
    end
```

### Validação de Token

```mermaid
flowchart TD
    A[Recebe Token] --> B{Decode JWT}
    B -->|Erro| C[401 Invalid Token]
    B -->|Sucesso| D{Verifica exp}
    D -->|Expirado| E[401 Expired]
    D -->|Válido| F{Existe sub?}
    F -->|Não| G[401 Invalid]
    F -->|Sim| H{sub é int válido?}
    H -->|Não| I[401 Invalid]
    H -->|Sim| J[Busca user no DB]
    J -->|Não existe| K[401 Not Found]
    J -->|Existe| L[Retorna User]
```

---

## Fluxo CRUD de Sessões de Estudo

### Criar Sessão

```mermaid
sequenceDiagram
    participant U as Usuário
    participant A as API (Sessions Router)
    participant S as Security Service
    participant M as Session Model
    participant DB as Database
    
    U->>A: POST /sessions/session<br/>(Bearer: token, session_data)
    A->>S: get_current_user(token)
    S-->>A: User atual
    A->>M: Session(topic, duration,<br/>notes, date, user_id)
    M->>DB: INSERT session
    DB-->>M: Session criada
    M-->>A: Session com ID
    A-->>U: 201 Created<br/>Session data
```

### Listar Sessões

```mermaid
sequenceDiagram
    participant U as Usuário
    participant A as API (Sessions Router)
    participant S as Security Service
    participant M as Session Model
    participant DB as Database
    
    U->>A: GET /sessions/sessions<br/>(Bearer: token, offset, limit, search)
    A->>S: get_current_user(token)
    S-->>A: User atual
    A->>M: SELECT WHERE user_id=?<br/>+ search filter
    M->>DB: Query com filtros
    DB-->>M: Sessions
    M-->>A: Lista de sessions
    A-->>U: 200 OK<br/>{sessions, offset, limit}
```

### Buscar Sessão por ID

```mermaid
flowchart TD
    A[GET /sessions/{id}] --> B[Autenticar usuário]
    B --> C[Buscar sessão no DB]
    C --> D{Sessão existe?}
    D -->|Não| E[404 Not Found]
    D -->|Sim| F{user_id == current_user.id?}
    F -->|Não| G[403 Forbidden]
    F -->|Sim| H[200 OK<br/>Session data]
```

### Atualizar Sessão

```mermaid
sequenceDiagram
    participant U as Usuário
    participant A as API (Sessions Router)
    participant S as Security Service
    participant M as Session Model
    participant DB as Database
    
    U->>A: PUT /sessions/{id}<br/>(Bearer: token, update_data)
    A->>S: get_current_user(token)
    S-->>A: User atual
    A->>M: GET session by ID
    M-->>A: Session
    A->>A: verify_ownership()
    alt Sem permissão
        A-->>U: 403 Forbidden
    else Com permissão
        A->>M: UPDATE session
        M->>DB: COMMIT
        DB-->>M: Session atualizada
        M-->>A: Session
        A-->>U: 200 OK
    end
```

### Deletar Sessão

```mermaid
flowchart TD
    A[DELETE /sessions/{id}] --> B[Autenticar usuário]
    B --> C[Buscar sessão no DB]
    C --> D{Sessão existe?}
    D -->|Não| E[404 Not Found]
    D -->|Sim| F{user_id == current_user.id?}
    F -->|Não| G[403 Forbidden]
    F -->|Sim| H[DELETE session]
    H --> I[COMMIT]
    I --> J[204 No Content]
```

---

## Fluxo de Segurança

### Hash de Senha

```mermaid
flowchart LR
    A[Senha Plain Text] --> B[pwdlib.hash<br/>Argon2]
    B --> C[Hash Armazenado]
    C --> D[Database]
    
    E[Login: Senha Input] --> F[pwdlib.verify]
    D --> F
    F --> G{Match?}
    G -->|Sim| H[Acesso Permitido]
    G -->|Não| I[Acesso Negado]
```

### Validação de Ownership

```mermaid
flowchart TD
    A[Requisição em recurso] --> B[Extrair user_id do recurso]
    B --> C[Extrair id do current_user]
    C --> D{user_id == current_user.id?}
    D -->|Sim| E[Acesso Permitido]
    D -->|Não| F[403 Forbidden<br/>Do not have permissions]
```

---

## Schemas Pydantic

### Hierarquia de Schemas

```mermaid
classDiagram
    class UserSchema {
        +username: str
        +email: EmailStr
        +password: str
    }
    
    class UserPublicSchema {
        +id: int
        +username: str
        +email: EmailStr
        +created_at: datetime
        +updated_at: datetime
    }
    
    class UserUpdateSchema {
        +username: Optional~str~
        +email: Optional~EmailStr~
        +password: Optional~str~
    }
    
    class UserListPublicSchema {
        +users: List~UserPublicSchema~
        +offset: int
        +limit: int
    }
    
    UserSchema --> UserPublicSchema : Create
    UserUpdateSchema --> UserPublicSchema : Update
    UserPublicSchema --> UserListPublicSchema : List
```

```mermaid
classDiagram
    class StudySessionSchema {
        +topic: str
        +duration_minutes: int
        +notes: Optional~str~
        +date: str
    }
    
    class StudySessionPublicSchema {
        +id: int
        +topic: str
        +duration_minutes: int
        +notes: Optional~str~
        +date: str
        +user_id: int
    }
    
    class StudySessionUpdateSchema {
        +topic: Optional~str~
        +duration_minutes: Optional~int~
        +notes: Optional~str~
        +date: Optional~str~
    }
    
    class StudySessionListPublicSchema {
        +sessions: List~StudySessionPublicSchema~
        +offset: int
        +limit: int
    }
    
    StudySessionSchema --> StudySessionPublicSchema : Create
    StudySessionUpdateSchema --> StudySessionPublicSchema : Update
    StudySessionPublicSchema --> StudySessionListPublicSchema : List
```

---

## Configurações do Sistema

### Settings

```mermaid
graph LR
    A[.env File] --> B[Pydantic Settings]
    B --> C[Settings Class]
    C --> D[DATABASE_URL]
    C --> E[JWT_SECRET_KEY]
    C --> F[JWT_ALGORITHM]
    C --> G[JWT_EXPIRATION_MINUTES]
    
    D --> H[Database Engine]
    E --> I[JWT Token]
    F --> I
    G --> I
```

---

## Próximos Passos

1. [Segurança](security.md) - Detalhes de autenticação e segurança
2. [Desenvolvimento](development.md) - Guia de desenvolvimento
3. [Deploy](deploy.md) - Instruções de implantação
