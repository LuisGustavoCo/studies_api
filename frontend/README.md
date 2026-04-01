# StudiesAPI — Frontend

Frontend para a [StudiesAPI](../README.md), desenvolvido em HTML, CSS e JavaScript puro.

## 🚀 Como usar

### 1. Inicie o backend

```bash
cd ..  # pasta raiz studies_api
poetry run fastapi dev studies_api/app.py
```

O backend estará em `http://127.0.0.1:8000`.

### 2. Sirva o frontend

Abra com um servidor local (para evitar restrições de CORS com `file://`):

**Opção A — Python (já instalado):**
```bash
cd frontend
python3 -m http.server 5500
```
Acesse: `http://localhost:5500`

**Opção B — VS Code Live Server:**
Clique com o botão direito em `index.html` → "Open with Live Server"

**Opção C — Node.js serve:**
```bash
npx serve frontend
```

## ✨ Funcionalidades

| Página | O que faz |
|--------|-----------|
| **Login / Cadastro** | Autenticação JWT com refresh automático |
| **Dashboard** | Estatísticas (total sessões, minutos, horas, tópico top), sessões recentes, gráfico por tópico |
| **Sessões** | CRUD completo — criar, editar, excluir, buscar, paginar |
| **Perfil** | Atualizar username/email/senha, excluir conta |

## 🗂 Estrutura

```
frontend/
├── index.html   # Estrutura da SPA (auth + app)
├── style.css    # Design system completo (dark mode, glassmorphism)
└── app.js       # Lógica de integração com a API
```
