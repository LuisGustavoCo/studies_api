# Deploy

Este documento descreve como implantar a StudiesAPI em diferentes ambientes de produção.

## Pré-requisitos para Deploy

### Requisitos do Servidor

- **Python**: 3.13 ou superior
- **Memória RAM**: Mínimo 512MB (recomendado 1GB+)
- **Armazenamento**: Mínimo 1GB livre
- **Sistema**: Linux (Ubuntu 20.04+ recomendado)

### Requisitos de Rede

- **Domínio**: Domínio próprio ou subdomínio
- **SSL/TLS**: Certificado para HTTPS
- **Portas**: 80 (HTTP), 443 (HTTPS)

---

## Preparação para Produção

### 1. Variáveis de Ambiente

Criar `.env.production`:

```bash
# Database (PostgreSQL recomendado)
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/studies_db

# JWT
JWT_SECRET_KEY=<gerar_chave_segura>
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=30

# Opcional
LOG_LEVEL=INFO
```

### 2. Gerar Chave Secreta

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 3. Instalar Dependências

```bash
# Instalar Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Instalar dependências de produção
poetry install --only main --no-dev
```

### 4. Executar Migrações

```bash
poetry run alembic upgrade head
```

---

## Deploy com Docker

### Dockerfile

```dockerfile
# Dockerfile
FROM python:3.13-slim

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Instalar Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/root/.local/bin:$PATH"

# Definir diretório de trabalho
WORKDIR /app

# Copiar arquivos de dependências
COPY pyproject.toml poetry.lock ./

# Instalar dependências
RUN poetry config virtualenvs.create false \
    && poetry install --only main --no-dev

# Copiar código fonte
COPY . .

# Expor porta
EXPOSE 8000

# Comando para iniciar
CMD ["uvicorn", "studies_api.app:app", "--host", "0.0.0.0", "--port", "8000"]
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://user:pass@db:5432/studies_db
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
      - JWT_ALGORITHM=HS256
      - JWT_EXPIRATION_MINUTES=30
    depends_on:
      - db
    restart: unless-stopped
    volumes:
      - ./logs:/app/logs

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=studies_db
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  postgres_data:
```

### Construir e Rodar

```bash
# Build
docker-compose build

# Rodar
docker-compose up -d

# Ver logs
docker-compose logs -f api

# Parar
docker-compose down
```

---

## Deploy em Servidor Linux (Ubuntu)

### 1. Configurar Servidor

```bash
# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Python e dependências
sudo apt install -y python3.13 python3.13-venv git nginx

# Instalar Poetry
curl -sSL https://install.python-poetry.org | python3 -
```

### 2. Clonar Projeto

```bash
cd /var/www
sudo git clone <repository_url> studies_api
sudo chown -R $USER:$USER studies_api
cd studies_api
```

### 3. Configurar Ambiente

```bash
# Instalar dependências
poetry install --only main --no-dev

# Criar .env
cp .env.example .env
nano .env  # Editar com configurações de produção

# Executar migrações
poetry run alembic upgrade head
```

### 4. Systemd Service

Criar `/etc/systemd/system/studies-api.service`:

```ini
[Unit]
Description=StudiesAPI
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/studies_api
Environment="PATH=/home/user/.local/bin"
ExecStart=/home/user/.local/bin/poetry run uvicorn studies_api.app:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

### 5. Iniciar Serviço

```bash
# Recarregar systemd
sudo systemctl daemon-reload

# Habilitar serviço
sudo systemctl enable studies-api

# Iniciar
sudo systemctl start studies-api

# Ver status
sudo systemctl status studies-api
```

### 6. Configurar Nginx

Criar `/etc/nginx/sites-available/studies-api`:

```nginx
server {
    listen 80;
    server_name api.seudominio.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 7. Habilitar Site

```bash
# Criar link simbólico
sudo ln -s /etc/nginx/sites-available/studies-api /etc/nginx/sites-enabled/

# Testar configuração
sudo nginx -t

# Recarregar Nginx
sudo systemctl reload nginx
```

### 8. Configurar SSL (Certbot)

```bash
# Instalar Certbot
sudo apt install -y certbot python3-certbot-nginx

# Obter certificado
sudo certbot --nginx -d api.seudominio.com

# Renovar automaticamente
sudo certbot renew --dry-run
```

---

## Deploy em Plataformas Cloud

### Railway

1. Conectar repositório GitHub
2. Configurar variáveis de ambiente
3. Deploy automático

**railway.json:**
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "poetry run uvicorn studies_api.app:app --host 0.0.0.0 --port $PORT",
    "restartPolicyType": "ON_FAILURE"
  }
}
```

### Render

1. Criar Web Service
2. Conectar repositório
3. Build Command: `poetry install --only main`
4. Start Command: `poetry run uvicorn studies_api.app:app --host 0.0.0.0 --port $PORT`

### Heroku

**Procfile:**
```
web: poetry run uvicorn studies_api.app:app --host 0.0.0.0 --port $PORT
```

**buildpacks:**
```bash
heroku buildpacks:add --index 1 https://github.com/moneymeets/python-poetry-buildpack
```

---

## Monitoramento

### Logs

```bash
# Systemd
sudo journalctl -u studies-api -f

# Docker
docker-compose logs -f api

# Nginx
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Health Check

```bash
# Verificar se API está respondendo
curl https://api.seudominio.com/health_check

# Expected: {"status": "OK"}
```

### Métricas

Configurar monitoramento:
- **Uptime**: UptimeRobot, Pingdom
- **Logs**: Papertrail, Loggly
- **Métricas**: Prometheus + Grafana
- **APM**: New Relic, Datadog, Sentry

---

## Backup

### Banco de Dados

```bash
# PostgreSQL backup
pg_dump -U user studies_db > backup_$(date +%Y%m%d).sql

# Restaurar
psql -U user studies_db < backup_20260319.sql
```

### Script de Backup Automático

```bash
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/studies_api"

# Backup do banco
pg_dump -U user studies_db | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# Manter últimos 7 backups
find $BACKUP_DIR -name "db_*.sql.gz" -mtime +7 -delete

echo "Backup completed: $DATE"
```

### Cron Job

```bash
# Editar crontab
crontab -e

# Adicionar backup diário às 3 AM
0 3 * * * /path/to/backup.sh
```

---

## CI/CD com GitHub Actions

### Workflow de Deploy

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Deploy to Server
      uses: appleboy/ssh-action@master
      with:
        host: ${{ secrets.SERVER_HOST }}
        username: ${{ secrets.SERVER_USER }}
        key: ${{ secrets.SSH_PRIVATE_KEY }}
        script: |
          cd /var/www/studies_api
          git pull origin main
          poetry install --only main --no-dev
          poetry run alembic upgrade head
          sudo systemctl restart studies-api
```

---

## Checklist de Deploy

### Pré-Deploy

- [ ] Testes passando
- [ ] Lint aprovado
- [ ] Variáveis de ambiente configuradas
- [ ] Banco de dados configurado
- [ ] Migrações criadas
- [ ] Chaves secretas geradas
- [ ] Domínio configurado
- [ ] SSL certificado

### Pós-Deploy

- [ ] Health check respondendo
- [ ] Endpoints testados
- [ ] Logs verificados
- [ ] Monitoramento configurado
- [ ] Backup configurado
- [ ] Documentação atualizada

---

## Troubleshooting

### Serviço não inicia

```bash
# Verificar logs
sudo journalctl -u studies-api -n 50

# Verificar se porta está livre
sudo lsof -i :8000

# Testar manualmente
poetry run uvicorn studies_api.app:app --host 0.0.0.0 --port 8000
```

### Erro de conexão com banco

```bash
# Verificar DATABASE_URL
echo $DATABASE_URL

# Testar conexão
poetry run python -c "
from studies_api.core.database import engine
import asyncio
async def test():
    async with engine.connect() as conn:
        print('OK')
asyncio.run(test())
"
```

### Nginx retornando 502

```bash
# Verificar se API está rodando
sudo systemctl status studies-api

# Verificar logs do Nginx
sudo tail -f /var/log/nginx/error.log

# Testar proxy
curl http://127.0.0.1:8000/health_check
```

---

## Próximos Passos

1. [Contribuição](contributing.md) - Como contribuir
2. [Release Notes](release-notes.md) - Histórico de versões
