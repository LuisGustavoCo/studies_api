# StudiesAPI - Documentação

Bem-vindo à documentação oficial da **StudiesAPI**, uma API RESTful desenvolvida em Python com FastAPI para gerenciamento de sessões de estudo e acompanhamento de métricas de aprendizado.

## 📋 Visão Geral

A StudiesAPI é uma aplicação backend projetada para ajudar estudantes a organizar e acompanhar suas sessões de estudo. A API permite:

- **Gerenciamento de Usuários**: Cadastro, autenticação e gerenciamento de contas
- **Sessões de Estudo**: CRUD completo para registrar sessões de estudo com tópico, duração e notas
- **Estatísticas**: Acompanhamento de métricas como total de sessões, tempo estudado e tópicos mais frequentes
- **Autenticação Segura**: JWT (JSON Web Tokens) para proteção dos endpoints

## 🎯 Funcionalidades Principais

| Funcionalidade | Descrição |
|---------------|-----------|
| Autenticação | Login com JWT e refresh de token |
| Usuários | CRUD completo com validações |
| Sessões | Registro e acompanhamento de estudos |
| Estatísticas | Métricas pessoais de estudo |
| Segurança | Hash de senhas e autorização por ownership |

## 📚 Estrutura da Documentação

| Arquivo | Descrição |
|---------|-----------|
| [`overview.md`](overview.md) | Visão geral detalhada do projeto |
| [`prerequisites.md`](prerequisites.md) | Pré-requisitos para desenvolvimento |
| [`installation.md`](installation.md) | Guia de instalação passo a passo |
| [`configuration.md`](configuration.md) | Configuração de variáveis de ambiente |
| [`guidelines.md`](guidelines.md) | Guidelines e padrões do projeto |
| [`structure.md`](structure.md) | Estrutura de diretórios e arquivos |
| [`api-endpoints.md`](api-endpoints.md) | Documentação completa da API |
| [`data-modeling.md`](data-modeling.md) | Modelagem de dados e arquitetura |
| [`security.md`](security.md) | Autenticação e segurança |
| [`development.md`](development.md) | Guia de desenvolvimento |
| [`testing.md`](testing.md) | Execução de testes |
| [`deploy.md`](deploy.md) | Instruções de deploy |
| [`contributing.md`](contributing.md) | Como contribuir |
| [`release-notes.md`](release-notes.md) | Histórico de versões |

## 🚀 Início Rápido

```bash
# Clonar repositório
git clone <repository-url>
cd studies_api

# Instalar dependências
poetry install

# Configurar variáveis de ambiente
cp .env.example .env

# Executar migrações
alembic upgrade head

# Iniciar servidor
poetry run fastapi dev studies_api/app.py
```

Acesse `http://127.0.0.1:8000/docs` para visualizar a documentação interativa da API.

## 📊 Tecnologias Utilizadas

- **Framework**: FastAPI
- **Banco de Dados**: SQLite (via SQLAlchemy Async)
- **ORM**: SQLAlchemy 2.0+
- **Autenticação**: JWT (PyJWT)
- **Hash de Senhas**: pwdlib (Argon2)
- **Migrações**: Alembic
- **Gerenciador de Pacotes**: Poetry
- **Linting/Formatting**: Ruff

## 📝 Licença

Este projeto é de uso pessoal/educacional.

---

**Versão da Documentação**: 0.1.0  
**Última Atualização**: Março de 2026
