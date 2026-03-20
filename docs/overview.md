# Visão Geral do Projeto

## Descrição

A **StudiesAPI** é uma API RESTful moderna e leve, desenvolvida com **FastAPI**, projetada para auxiliar estudantes no gerenciamento e acompanhamento de suas sessões de estudo. A aplicação permite registrar sessões de estudo com detalhes como tópico, duração, notas e data, além de fornecer estatísticas pessoais para acompanhamento do progresso acadêmico.

## Objetivos

1. **Organização**: Permitir que usuários registrem e organizem suas sessões de estudo de forma estruturada
2. **Acompanhamento**: Fornecer métricas e estatísticas sobre o tempo e tópicos estudados
3. **Segurança**: Garantir que cada usuário tenha acesso apenas aos seus próprios dados
4. **Performance**: Utilizar operações assíncronas para melhor desempenho

## Funcionalidades

### Autenticação e Autorização

- **Login**: Autenticação via email e senha com geração de JWT token
- **Refresh Token**: Atualização de token de acesso sem necessidade de relogin
- **Autorização**: Proteção de endpoints que requerem autenticação
- **Ownership**: Validação de posse de recursos (usuário só acessa suas sessões)

### Gerenciamento de Usuários

| Operação | Endpoint | Descrição |
|----------|----------|-----------|
| Criar | `POST /api/v1/users/` | Cadastro de novo usuário |
| Listar | `GET /api/v1/users/` | Listagem de usuários com paginação |
| Buscar | `GET /api/v1/users/{id}` | Buscar usuário por ID |
| Atualizar | `PUT /api/v1/users/{id}` | Atualizar dados do usuário |
| Deletar | `DELETE /api/v1/users/{id}` | Remover usuário |

### Gerenciamento de Sessões de Estudo

| Operação | Endpoint | Descrição |
|----------|----------|-----------|
| Criar | `POST /api/v1/sessions/session` | Registrar nova sessão |
| Listar | `GET /api/v1/sessions/sessions` | Listar sessões do usuário |
| Buscar | `GET /api/v1/sessions/sessions/{id}` | Buscar sessão por ID |
| Atualizar | `PUT /api/v1/sessions/sessions/{id}` | Atualizar sessão |
| Deletar | `DELETE /api/v1/sessions/sessions/{id}` | Remover sessão |

### Estatísticas

| Operação | Endpoint | Descrição |
|----------|----------|-----------|
| Obter | `GET /api/v1/stats/` | Estatísticas de estudo do usuário |

**Métricas Disponíveis:**
- `total_sessions`: Total de sessões registradas
- `total_minutes`: Soma total de minutos estudados
- `most_studied_topic`: Tópico mais estudado

## Arquitetura

A API segue a arquitetura **RESTful** com organização em camadas:

```
┌─────────────────────────────────────────────────────────┐
│                      Cliente HTTP                        │
│              (Browser, Mobile, Postman, etc.)            │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                    FastAPI Application                   │
│                    (app.py - Router)                     │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                       Routers                            │
│            (auth, users, sessions, stats)                │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                    Core Services                         │
│          (database, security, settings)                  │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                   Models & Schemas                       │
│         (SQLAlchemy Models, Pydantic Schemas)            │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                     Database                             │
│                  (SQLite via Async)                      │
└─────────────────────────────────────────────────────────┘
```

## Stack Tecnológico

### Backend
- **Python 3.13+**: Linguagem de programação
- **FastAPI 0.135+**: Framework web assíncrono
- **SQLAlchemy 2.0+**: ORM com suporte async
- **Alembic 1.18+**: Gerenciamento de migrações

### Segurança
- **PyJWT 2.12+**: Geração e validação de tokens JWT
- **pwdlib[argon2] 0.3+**: Hash de senhas com Argon2

### Configuração
- **Pydantic Settings 2.13+**: Gerenciamento de configurações
- **python-dotenv**: Carregamento de variáveis de ambiente

### Desenvolvimento
- **Ruff 0.15+**: Linter e formatter
- **Poetry**: Gerenciamento de dependências e virtualenv

### Documentação
- **MKDocs 1.6+**: Gerador de documentação
- **MKDocs Material 9.7+**: Tema para documentação

## Diferenciais

1. **Assíncrono**: Utiliza `async/await` em todas as operações de I/O
2. **Type Safety**: Tipagem completa com Pydantic e type hints
3. **Validações**: Validações de dados nos schemas (min length, email, etc.)
4. **Documentação Automática**: Swagger UI e ReDoc integrados
5. **Código Limpo**: Segue padrões de código limpo e boas práticas

## Casos de Uso

### Para Estudantes
- Registrar sessões de estudo diárias
- Acompanhar tempo total dedicado aos estudos
- Identificar tópicos que precisam de mais atenção
- Manter histórico de estudos com notas

### Para Desenvolvedores
- Base para projetos de estudo de FastAPI
- Exemplo de implementação de autenticação JWT
- Referência para CRUD assíncrono com SQLAlchemy

## Limitações Atuais

- Apenas SQLite como banco de dados (facilmente substituível)
- Sem testes automatizados implementados
- Sem rate limiting
- Sem paginação avançada (apenas offset/limit)

## Roadmap

- [ ] Adicionar testes unitários e de integração
- [ ] Implementar rate limiting
- [ ] Adicionar suporte a múltiplos bancos de dados
- [ ] Implementar refresh token com blacklist
- [ ] Adicionar exportação de dados (CSV, JSON)
- [ ] Dashboard de estatísticas avançadas
