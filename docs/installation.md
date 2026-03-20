# Instalação

Este guia descreve o processo completo de instalação da StudiesAPI em seu ambiente de desenvolvimento.

## Passo a Passo

### 1. Clonar o Repositório

```bash
# Clonar repositório
git clone <URL_DO_REPOSITORIO>

# Acessar diretório do projeto
cd studies_api
```

### 2. Verificar Versão do Python

```bash
# Verificar versão instalada
python --version
# ou
python3 --version

# Deve ser Python 3.13 ou superior
```

### 3. Instalar Dependências com Poetry

```bash
# Instalar todas as dependências (incluindo grupo dev)
poetry install

# Ou apenas dependências de produção
poetry install --only main
```

**O que o Poetry faz:**
- Cria um ambiente virtual isolado
- Instala todas as dependências do `pyproject.toml`
- Gera/atualiza o `poetry.lock`

### 4. Configurar Variáveis de Ambiente

```bash
# Criar arquivo .env a partir do exemplo
cp .env.example .env

# Editar o arquivo .env com suas configurações
# (veja a seção de Configuração para detalhes)
```

### 5. Executar Migrações do Banco de Dados

```bash
# Ativar ambiente virtual (opcional, pois poetry run já ativa)
poetry shell

# Executar migrações
poetry run alembic upgrade head
```

**Saída esperada:**
```
INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> <revision_id>, <message>
```

### 6. Iniciar o Servidor de Desenvolvimento

```bash
# Método 1: Usando taskipy (recomendado)
poetry run task run

# Método 2: Diretamente com FastAPI
poetry run fastapi dev studies_api/app.py

# Método 3: Usando o script run.sh (Linux/macOS)
./run.sh
```

**Saída esperada:**
```
INFO:     Will watch for changes in these directories: /path/to/studies_api
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

### 7. Verificar Instalação

Acesse no navegador:
- **API**: http://127.0.0.1:8000
- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc
- **Health Check**: http://127.0.0.1:8000/health_check

## Estrutura de Dependências

### Dependências de Produção

| Pacote | Versão | Finalidade |
|--------|--------|-----------|
| fastapi[standard] | 0.135.x | Framework web |
| pydantic | 2.12.x | Validação de dados |
| sqlalchemy[asyncio] | 2.0.x | ORM assíncrono |
| aiosqlite | 0.22.x | Driver SQLite async |
| pydantic-settings | 2.13.x | Configurações |
| alembic | 1.18.x | Migrações |
| greenlet | 3.3.x | Suporte async SQLAlchemy |
| pwdlib[argon2] | 0.3.x | Hash de senhas |
| pyjwt | 2.12.x | Tokens JWT |
| mkdocs | 1.6.x | Documentação |
| mkdocs-material | 9.7.x | Tema docs |
| pymdown-extensions | 10.21.x | Extensões Markdown |

### Dependências de Desenvolvimento

| Pacote | Versão | Finalidade |
|--------|--------|-----------|
| ruff | 0.15.x | Linter/Formatter |
| taskipy | 1.14.x | Task runner |

## Comandos Úteis

### Ambiente Virtual

```bash
# Ativar ambiente virtual
poetry shell

# Sair do ambiente virtual
exit

# Executar comando sem ativar shell
poetry run <comando>
```

### Gerenciamento de Dependências

```bash
# Adicionar nova dependência
poetry add <pacote>

# Adicionar dependência de desenvolvimento
poetry add --group dev <pacote>

# Remover dependência
poetry remove <pacote>

# Atualizar dependências
poetry update

# Ver árvore de dependências
poetry show --tree
```

### Tarefas Disponíveis

```bash
# Rodar linter
poetry run task lint

# Formatar código
poetry run task format

# Iniciar servidor
poetry run task run

# Servir documentação
poetry run task docs
```

## Instalação em Diferentes Sistemas

### Linux (Ubuntu/Debian)

```bash
# Instalar pré-requisitos
sudo apt update
sudo apt install -y python3.13 python3.13-venv git curl

# Instalar Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Clonar e instalar
git clone <URL>
cd studies_api
poetry install
```

### macOS

```bash
# Instalar Python via Homebrew
brew install python@3.13 git

# Instalar Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Clonar e instalar
git clone <URL>
cd studies_api
poetry install
```

### Windows (WSL2)

```bash
# No WSL (Ubuntu)
sudo apt update
sudo apt install -y python3.13 python3.13-venv git curl

# Instalar Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Clonar e instalar
git clone <URL>
cd studies_api
poetry install
```

### Windows (Nativo)

```powershell
# Instalar Python do site oficial
# Instalar Poetry
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -

# Clonar repositório
git clone <URL>
cd studies_api

# Instalar dependências
poetry install
```

## Troubleshooting

### Erro: Python version not found

```bash
# Verificar versões disponíveis
poetry env list

# Especificar versão do Python
poetry env use python3.13
```

### Erro: ModuleNotFoundError

```bash
# Reinstalar dependências
poetry install --no-cache
```

### Erro: Database locked (SQLite)

```bash
# Remover arquivo de banco travado
rm *.db

# Reexecutar migrações
poetry run alembic upgrade head
```

### Erro: Port already in use

```bash
# Matar processo na porta 8000
lsof -ti:8000 | xargs kill -9

# Ou usar outra porta
poetry run fastapi dev studies_api/app.py --port 8001
```

### Poetry lento na instalação

```bash
# Limpar cache
poetry cache clear pypi --all

# Reinstalar
poetry install
```

## Validação Final

Execute os seguintes comandos para validar a instalação:

```bash
# Verificar se Poetry instalou corretamente
poetry --version

# Verificar dependências instaladas
poetry show

# Testar import do projeto
poetry run python -c "from studies_api.app import app; print('OK')"

# Iniciar servidor
poetry run fastapi dev studies_api/app.py
```

Se tudo estiver correto, você verá a mensagem de servidor rodando em `http://127.0.0.1:8000`.

## Próximos Passos

1. [Configuração](configuration.md) - Configurar variáveis de ambiente
2. [API Endpoints](api-endpoints.md) - Explorar endpoints disponíveis
3. [Desenvolvimento](development.md) - Iniciar desenvolvimento
