# Contribuição

Este documento descreve como contribuir para o desenvolvimento da StudiesAPI.

## Como Contribuir

Existem várias formas de contribuir para o projeto:

1. **Reportar bugs**
2. **Sugerir novas funcionalidades**
3. **Enviar pull requests com correções**
4. **Melhorar documentação**
5. **Revisar código de outros contribuidores**

---

## Reportar Bugs

### Onde Reportar

- **GitHub Issues**: [Issues do Projeto](https://github.com/LuisGustavoCo/studies_api/issues)

### Template de Bug Report

```markdown
### Descrição
Descrição clara e concisa do bug.

### Passos para Reproduzir
1. Configurar ambiente '...'
2. Executar comando '...'
3. Fazer request '...'
4. Ver erro

### Comportamento Esperado
O que deveria acontecer.

### Comportamento Atual
O que está acontecendo.

### Ambiente
- OS: [Ubuntu 22.04, macOS 13, Windows 11]
- Python: [3.13.0]
- Versão da API: [0.1.0]

### Logs
```
<cole os logs relevantes aqui>
```

### Screenshots
Se aplicável, adicione screenshots.
```

---

## Sugerir Funcionalidades

### Template de Feature Request

```markdown
### Problema Relacionado
Existe um problema que esta funcionalidade resolve?

### Solução Proposta
Descrição clara do que você quer que aconteça.

### Alternativas Consideradas
Outras soluções que você considerou.

### Contexto Adicional
Qualquer outro contexto, screenshots ou exemplos.
```

---

## Desenvolvimento

### Setup Inicial

```bash
# 1. Fork do repositório
# No GitHub, clique em "Fork"

# 2. Clonar seu fork
git clone https://github.com/SEU_USUARIO/studies_api.git
cd studies_api

# 3. Adicionar upstream
git remote add upstream https://github.com/ORIGINAL_OWNER/studies_api.git

# 4. Instalar dependências
poetry install

# 5. Configurar ambiente
cp .env.example .env
# Editar .env

# 6. Executar migrações
poetry run alembic upgrade head
```

### Workflow de Contribuição

```bash
# 1. Atualizar fork
git checkout main
git pull upstream main

# 2. Criar branch para feature/fix
git checkout -b feature/minha-feature

# 3. Implementar mudanças
# Fazer commits seguindo Conventional Commits

# 4. Manter branch atualizada
git fetch upstream
git rebase upstream main

# 5. Rodar lint e format
poetry run task lint
poetry run task format

# 6. Testar localmente
poetry run task run

# 7. Commit final
git commit -m "feat: adicionar nova funcionalidade"

# 8. Push para seu fork
git push origin feature/minha-feature

# 9. Criar Pull Request
# No GitHub, vá para seu fork e clique em "Compare & pull request"
# https://github.com/LuisGustavoCo/studies_api/pulls
```

---

## Padrões de Código

### Conventional Commits

Seguir o padrão [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

#### Tipos

| Tipo | Descrição |
|------|-----------|
| `feat` | Nova funcionalidade |
| `fix` | Correção de bug |
| `docs` | Documentação |
| `style` | Formatação, linting |
| `refactor` | Refatoração de código |
| `test` | Adicionar ou corrigir testes |
| `chore` | Configuração, build, ferramentas |

#### Exemplos

```bash
feat(sessions): add search by topic
fix(auth): resolve token expiration validation
docs: update API endpoints documentation
style: format code with ruff
refactor(database): extract connection logic
test: add unit tests for auth router
chore: update dependencies
```

### Code Style

#### Formatação

```bash
# Formatar código
poetry run task format

# Ou diretamente
poetry run ruff format studies_api/
```

#### Lint

```bash
# Verificar
poetry run task lint

# Corrigir automaticamente
poetry run ruff check --fix studies_api/
```

#### Type Hints

Sempre usar type hints:

```python
# ✅ Correto
def get_user(user_id: int, db: AsyncSession) -> User:
    pass

# ❌ Incorreto
def get_user(user_id, db):
    pass
```

#### Docstrings

Documentar funções públicas:

```python
def create_access_token(data: Dict) -> str:
    """
    Cria um token de acesso JWT.
    
    Args:
        data: Dados a serem codificados no token.
    
    Returns:
        Token JWT codificado.
    """
    # Implementação
```

---

## Pull Request

### Checklist de PR

Antes de criar um PR, verifique:

- [ ] Código formatado (`poetry run task format`)
- [ ] Lint passando (`poetry run task lint`)
- [ ] Type hints em funções
- [ ] Docstrings em funções públicas
- [ ] Testes manuais realizados
- [ ] Migrações criadas (se aplicável)
- [ ] Documentação atualizada (se aplicável)
- [ ] Commit messages no padrão Conventional Commits
- [ ] Branch atualizada com main

### Template de PR

```markdown
## Descrição
Descrição clara das mudanças.

## Tipo de Mudança
- [ ] Bug fix
- [ ] Nova funcionalidade
- [ ] Refatoração
- [ ] Documentação
- [ ] Outro

## Issue Relacionada
Fixes #<número_da_issue>

## Como Testar
Passos para testar as mudanças:
1. ...
2. ...

## Checklist
- [ ] Meu código segue as guidelines do projeto
- [ ] Adicionei/atualizei documentação
- [ ] Testei localmente
- [ ] Não há breaking changes

## Screenshots
Se aplicável.
```

### Processo de Review

1. **Criação**: Contribuidor cria PR
2. **CI**: Checks automáticos rodam (lint, testes)
3. **Review**: Mantenedores revisam código
4. **Feedback**: Comentários e solicitações de mudança
5. **Ajustes**: Contribuidor faz ajustes
6. **Aprovação**: PR aprovado
7. **Merge**: Merge para main

---

## Diretrizes de Código

### Imports

```python
# Ordem dos imports
# 1. Standard library
from datetime import datetime
from typing import List, Optional

# 2. Third-party
from fastapi import APIRouter, Depends
from sqlalchemy import select

# 3. First-party
from studies_api.core.database import get_connection
from studies_api.models.users import User
```

### Nomenclatura

```python
# Classes: PascalCase
class UserSchema(BaseModel):
    pass

# Funções/variáveis: snake_case
def get_current_user():
    pass

user_id = 123

# Constantes: UPPER_SNAKE_CASE
JWT_ALGORITHM = 'HS256'

# Private: prefixo _
def _internal_helper():
    pass
```

### Tratamento de Erros

```python
# Usar HTTPException para erros HTTP
from fastapi import HTTPException, status

if not user:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail='User Not Found',
    )
```

### Validações

```python
# Usar validadores do Pydantic
from pydantic import BaseModel, field_validator

class UserSchema(BaseModel):
    username: str
    
    @field_validator('username')
    def username_min_length(cls, v):
        if len(v) < 6:
            raise ValueError('Username must be greater than 6 characters.')
        return v
```

---

## Documentação

### Atualizar Documentação

```bash
# Editar arquivo em docs/
# Exemplo: docs/api-endpoints.md

# Servir documentação localmente
poetry run task docs

# Acessar http://127.0.0.1:8001
```

### Padrão de Documentação

- Arquivos em **inglês** (nome)
- Conteúdo em **português brasileiro**
- Usar Markdown
- Incluir exemplos de código
- Usar diagramas Mermaid quando aplicável

---

## Código de Conduta

### Nossas Responsabilidades

- Usar linguagem acolhedora e inclusiva
- Respeitar diferentes pontos de vista
- Aceitar críticas construtivas
- Focar no que é melhor para a comunidade
- Mostrar empatia com outros membros

### Comportamentos Inaceitáveis

- Uso de linguagem ou imagens sexuais
- Trolling, comentários insultuosos
- Assédio público ou privado
- Publicar informações privadas de outros
- Outra conduta inadequada

---

## Reconhecimento

Contribuidores serão reconhecidos em:

1. **README.md**: Lista de contribuidores
2. **Release Notes**: Menção em releases
3. **GitHub**: Contribuições no perfil do projeto

---

## Dúvidas?

### Canais de Comunicação

- **GitHub Issues**: Dúvidas técnicas
- **GitHub Discussions**: Discussões gerais
- **Email**: gustavoocorreia2005@gmail.com

### Recursos Úteis

- [Documentação do Projeto](index.md)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [SQLAlchemy Docs](https://docs.sqlalchemy.org/)
- [Pydantic Docs](https://docs.pydantic.dev/)

---

## Licença

Ao contribuir, você concorda que suas contribuições serão licenciadas sob a mesma licença do projeto.

---

## Obrigado por Contribuir! 🎉

Sua contribuição ajuda a tornar a StudiesAPI melhor para todos!
