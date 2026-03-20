# Pré-requisitos

Esta seção descreve todos os pré-requisitos necessários para desenvolver, testar e executar a StudiesAPI.

## Sistema Operacional

A API é compatível com os principais sistemas operacionais:

- **Linux**: Ubuntu 20.04+, Debian 10+, Fedora 33+
- **macOS**: macOS 11+ (Big Sur ou superior)
- **Windows**: Windows 10+ (recomendado WSL2 para desenvolvimento)

## Python

### Versão Requerida

- **Python 3.13** ou superior
- **Python < 4.0** (conforme especificado no `pyproject.toml`)

### Instalação do Python

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install python3.13 python3.13-venv python3.13-dev
```

#### macOS
```bash
# Usando Homebrew
brew install python@3.13
```

#### Windows
```bash
# Baixe o instalador em https://www.python.org/downloads/
# Marque a opção "Add Python to PATH" durante a instalação
```

### Verificação
```bash
python --version
# ou
python3 --version
```

## Poetry

O **Poetry** é o gerenciador de dependências e ambientes virtuais utilizado no projeto.

### Instalação

#### Método Recomendado (Linux/macOS/Windows)
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

#### Adicionar ao PATH

**Linux/macOS:**
```bash
export PATH="$HOME/.local/bin:$PATH"
```

**Windows (PowerShell):**
```powershell
$env:PATH = "$env:USERPROFILE\.local\bin;$env:PATH"
```

### Verificação
```bash
poetry --version
```

## Git

Necessário para clonar o repositório e gerenciar versões.

### Instalação

**Linux:**
```bash
sudo apt install git
```

**macOS:**
```bash
brew install git
```

**Windows:**
```bash
# Baixe em https://git-scm.com/download/win
```

### Configuração
```bash
git config --global user.name "Seu Nome"
git config --global user.email "seu.email@example.com"
```

### Verificação
```bash
git --version
```

## Editor de Código / IDE

### Opções Recomendadas

| Editor | Extensões Recomendadas |
|--------|----------------------|
| **VS Code** | Python, Pylance, Ruff, GitLens |
| **PyCharm** | Plugins nativos do Python |
| **Neovim/Vim** | python-mode, coc.nvim, ale |

### Configuração VS Code

Arquivo `.vscode/settings.json` (já incluso no projeto):
```json
{
  "python.formatting.provider": "ruff",
  "python.linting.enabled": true,
  "python.linting.ruffEnabled": true,
  "[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff",
    "editor.formatOnSave": true
  }
}
```

## Banco de Dados

### SQLite

O projeto utiliza **SQLite** como banco de dados padrão (via SQLAlchemy Async).

- **Vantagens**: Não requer instalação separada, embutido no Python
- **Limitações**: Não recomendado para produção com alto tráfego

### Bancos Suportados (Alternativos)

A API pode ser configurada para usar outros bancos suportados pelo SQLAlchemy:

- PostgreSQL
- MySQL
- MariaDB

## Ferramentas de Desenvolvimento

### Ruff

Já configurado no projeto via Poetry (grupo dev):

- **Linter**: Verificação de código
- **Formatter**: Formatação automática

### Taskipy

Gerenciador de tarefas via `pyproject.toml`:

```toml
[tool.taskipy.tasks]
lint = 'ruff check'
pre_format = 'ruff check --fix'
format = 'ruff format'
run = 'fastapi dev studies_api/app.py'
docs = 'mkdocs serve -a 127.0.0.1:8001'
```

## Ferramentas Opcionais

### HTTP Client

Para testar a API:

- **cURL**: CLI para requisições HTTP
- **HTTPie**: Alternativa moderna ao cURL
- **Postman**: Interface gráfica
- **Insomnia**: Alternativa ao Postman
- **Browser**: Acesso a `/docs` para Swagger UI

### Docker (Opcional)

Para containerização:

```bash
# Instale o Docker Desktop ou Docker Engine
docker --version
```

## Verificação de Todos os Pré-requisitos

Execute o script abaixo para verificar se tudo está instalado:

```bash
# Verificar Python
python --version

# Verificar Poetry
poetry --version

# Verificar Git
git --version

# Verificar pip
pip --version
```

## Resolução de Problemas Comuns

### Python não encontrado
```bash
# Linux/macOS
which python3
which python

# Windows
where python
```

### Poetry não encontrado
```bash
# Adicionar ao PATH manualmente
export PATH="$HOME/.local/bin:$PATH"
```

### Permissões no Linux/macOS
```bash
chmod +x run.sh
```

### Conflito de Versões do Python
```bash
# Usar pyenv para gerenciar múltiplas versões
brew install pyenv
pyenv install 3.13.0
pyenv local 3.13.0
```

## Próximos Passos

Após instalar todos os pré-requisitos, prossiga para:

1. [Instalação](installation.md) - Clonar e instalar dependências
2. [Configuração](configuration.md) - Configurar variáveis de ambiente
