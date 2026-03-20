# Configuração do Projeto

Este documento descreve como configurar corretamente a StudiesAPI para execução em diferentes ambientes.

## Variáveis de Ambiente

A configuração da aplicação é feita através do arquivo `.env`, que deve ser criado na raiz do projeto.

### Arquivo .env

Crie um arquivo `.env` na raiz do projeto com o seguinte conteúdo:

```bash
# Database
DATABASE_URL=sqlite+aiosqlite:///./studies.db

# JWT Settings
JWT_SECRET_KEY=sua_chave_secreta_muito_segura_aqui
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=30
```

### Descrição das Variáveis

| Variável | Descrição | Tipo | Obrigatória | Valor Padrão |
|----------|-----------|------|-------------|--------------|
| `DATABASE_URL` | URL de conexão com o banco de dados | string | Sim | - |
| `JWT_SECRET_KEY` | Chave secreta para criptografia JWT | string | Sim | - |
| `JWT_ALGORITHM` | Algoritmo de criptografia JWT | string | Não | `HS256` |
| `JWT_EXPIRATION_MINUTES` | Tempo de expiração do token em minutos | int | Não | `30` |

## Configuração do Banco de Dados

### SQLite (Desenvolvimento)

```bash
DATABASE_URL=sqlite+aiosqlite:///./studies.db
```

**Vantagens:**
- Não requer instalação adicional
- Ideal para desenvolvimento e testes
- Arquivo único

**Desvantagens:**
- Não recomendado para produção com alto tráfego
- Limitações de concorrência

### PostgreSQL (Produção)

```bash
DATABASE_URL=postgresql+asyncpg://usuario:senha@localhost:5432/studies_db
```

**Pré-requisitos:**
```bash
# Instalar driver async
poetry add asyncpg
```

### MySQL/MariaDB (Produção)

```bash
DATABASE_URL=mysql+aiomysql://usuario:senha@localhost:3306/studies_db
```

**Pré-requisitos:**
```bash
# Instalar driver async
poetry add aiomysql
```

## Configuração JWT

### Gerar Chave Secreta

**Opção 1 - Python:**
```bash
poetry run python -c "import secrets; print(secrets.token_urlsafe(32))"
```

**Opção 2 - OpenSSL:**
```bash
openssl rand -base64 32
```

**Opção 3 - Linux:**
```bash
cat /dev/urandom | head -c 32 | base64
```

### Melhores Práticas JWT

1. **Use chaves longas**: Mínimo de 32 caracteres
2. **Nunca commit a chave**: Mantenha `.env` no `.gitignore`
3. **Rotação de chaves**: Troque periodicamente em produção
4. **Ambientes diferentes**: Use chaves diferentes por ambiente

## Configuração por Ambiente

### Desenvolvimento (.env.development)

```bash
DATABASE_URL=sqlite+aiosqlite:///./dev_studies.db
JWT_SECRET_KEY=dev_secret_key_change_in_production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=60
```

### Testes (.env.test)

```bash
DATABASE_URL=sqlite+aiosqlite:///./test_studies.db
JWT_SECRET_KEY=test_secret_key_for_testing_only
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=5
```

### Produção (.env.production)

```bash
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/studies_db
JWT_SECRET_KEY=<GERAR_CHAVE_SEGURA>
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=30
```

## Carregamento de Configurações

O carregamento é feito automaticamente pela classe `Settings`:

```python
# studies_api/core/settings.py
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

    DATABASE_URL: str
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = 'HS256'
    JWT_EXPIRATION_MINUTES: int = 30
```

### Uso no Código

```python
from studies_api.core.settings import Settings

settings = Settings()
print(settings.DATABASE_URL)
print(settings.JWT_SECRET_KEY)
```

## Configuração do Alembic

O Alembic é configurado através do `alembic.ini`:

```ini
[alembic]
script_location = %(here)s/migrations
prepend_sys_path = .
sqlalchemy.url = driver://user:pass@localhost/dbname
```

### Configurar URL do Banco no Alembic

Edite `migrations/env.py` para usar as configurações do projeto:

```python
from studies_api.core.settings import Settings

config.set_main_option(
    "sqlalchemy.url",
    Settings().DATABASE_URL,
)
```

## Validação de Configuração

### Script de Validação

Crie um script para validar a configuração:

```python
# validate_config.py
from studies_api.core.settings import Settings

try:
    settings = Settings()
    print("✓ DATABASE_URL configurado")
    print("✓ JWT_SECRET_KEY configurado")
    print(f"✓ JWT_ALGORITHM: {settings.JWT_ALGORITHM}")
    print(f"✓ JWT_EXPIRATION_MINUTES: {settings.JWT_EXPIRATION_MINUTES}")
except Exception as e:
    print(f"✗ Erro na configuração: {e}")
```

### Testar Conexão

```bash
# Testar conexão com banco de dados
poetry run python -c "
from studies_api.core.database import engine
import asyncio

async def test():
    async with engine.connect() as conn:
        print('Conexão bem-sucedida!')

asyncio.run(test())
"
```

## Segurança

### Arquivo .env

**NUNCA** commit o arquivo `.env`:

```bash
# .gitignore (já configurado)
.env
.env.*
!.env.example
```

### .env.example

Mantenha um arquivo de exemplo versionado:

```bash
# .env.example
DATABASE_URL=sqlite+aiosqlite:///./studies.db
JWT_SECRET_KEY=CHANGE_ME_IN_PRODUCTION
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=30
```

### Permissões do Arquivo

```bash
# Linux/macOS - Restringir permissões
chmod 600 .env
```

## Variáveis Opcionais

### Debug Mode

```bash
# Para habilitar modo debug (se implementado)
DEBUG=true
```

### Log Level

```bash
# Níveis: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL=INFO
```

### CORS

```bash
# Origens permitidas (se implementado)
CORS_ORIGINS=http://localhost:3000,https://meudominio.com
```

## Troubleshooting

### Erro: Settings not found

```bash
# Verificar se .env existe
ls -la .env

# Verificar encoding do arquivo
file .env
```

### Erro: Database URL invalid

```bash
# Verificar formato da URL
# Formato: dialect+driver://username:password@host:port/database
```

### Erro: JWT configuration error

```bash
# Verificar se JWT_SECRET_KEY está definida
# Verificar se JWT_ALGORITHM é suportado (HS256, HS384, HS512)
```

## Checklist de Configuração

- [ ] Criar arquivo `.env` na raiz do projeto
- [ ] Configurar `DATABASE_URL` válido
- [ ] Gerar `JWT_SECRET_KEY` segura
- [ ] Definir `JWT_ALGORITHM` (padrão: HS256)
- [ ] Definir `JWT_EXPIRATION_MINUTES`
- [ ] Verificar se `.env` está no `.gitignore`
- [ ] Criar `.env.example` para documentação
- [ ] Testar conexão com banco de dados
- [ ] Executar migrações (`alembic upgrade head`)

## Próximos Passos

1. [Guidelines](guidelines.md) - Padrões de código
2. [Estrutura](structure.md) - Organização do projeto
3. [API Endpoints](api-endpoints.md) - Documentação da API
