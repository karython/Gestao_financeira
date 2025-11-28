# Gestão Financeira - API

Sistema de Gestão Financeira com backend em FastAPI, banco de dados relacional gerenciado via SQLAlchemy + Alembic e suporte a geração de relatórios em PDF e envio por e-mail.

## 🔎 Visão geral

Este projeto fornece um backend para controlar categorias, receitas, despesas (fixas e variáveis), gerar relatórios (JSON / PDF) e enviar relatórios por e-mail. A autenticação é por JWT e há endpoints para analytics e painel de resumo.

Principais recursos:
- Autenticação (registro/login/logout) com JWT
- CRUD de categorias, lançamentos (expenses), despesas fixas
- Cadastro e gestão de receitas (fixas e variáveis)
- Geração de relatórios (JSON e PDF) e envio por e-mail
- Endpoints informativos para dashboard/analytics

## 🧭 Estrutura do projeto

- `app.py` — Entrypoint FastAPI (lifespan, CORS, middleware)
- `api/api/v1/router.py` — Roteamento das rotas da API
- `api/api/v1/endpoints/` — Handlers por recurso (auth, categories, expenses, etc.)
- `api/models/` — Modelos SQLAlchemy (User, Expense, Category, FixedExpense, Income, etc.)
- `api/schemas/` — Schemas Pydantic (payloads e responses)
- `api/db/` — Configuração do SQLAlchemy e sessão assíncrona
- `api/services/` — Serviços utilitários (PDF/email)
- `alembic/` — Migrations (há versões de migração no repositório)

## 🧰 Tecnologias

- Python + FastAPI
- SQLAlchemy (async) + aiomysql
- Alembic para migrações
- FPDF para geração de PDF
- aiosmtplib para envio de e-mail
- JWT (python-jose) e passlib/bcrypt para segurança

## 📦 Instalação

1. Crie e ative um virtualenv (recomendado):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Instale as dependências

```powershell
pip install -r requirements.txt
```

3. Crie e configure um arquivo `.env` na raiz com as variáveis de ambiente importantes (exemplo abaixo).

## ⚙️ Variáveis de ambiente (exemplo `.env`)

- DATABASE_URL — URL de conexão (ex: `mysql+aiomysql://user:pass@host:3306/dbname`)
- SECRET_KEY — Chave secreta JWT
- SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD — Configuração para envio de e-mail
- EMAILS_FROM_EMAIL — endereço "from" usado para enviar relatórios
- ACCESS_TOKEN_EXPIRE_MINUTES — validade do token (padrão 30)
- CORS_ORIGINS — orígens permitidas para CORS

Exemplo mínimo:

```
DATABASE_URL=mysql+aiomysql://user:password@localhost:3306/db
SECRET_KEY=uma-chave-secreta
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=seu-email
SMTP_PASSWORD=sua-senha
EMAILS_FROM_EMAIL=noreply@financeiro.com
```

> Atenção: NÃO comite segredos em repositório público.

## ▶️ Como rodar localmente

```powershell
# no prompt do projeto com o venv ativo
uvicorn app:app --reload
# ou rode diretamente (app.py já chama uvicorn quando executado)
python app.py
```

A API será exposta por padrão em `http://127.0.0.1:8000` e a OpenAPI estará em `/api/openapi.json` (pois a aplicação usa `settings.API_V1_STR` = `/api`).

## 📚 Migrações

O repositório contém configuração do Alembic e scripts em `alembic/versions/`.

Comandos típicos (com `alembic` instalado):

```powershell
alembic revision --autogenerate -m "mensagem"
alembic upgrade head
```

> Dependendo do layout do projeto (import paths) você pode precisar ajustar `alembic.ini` e `env.py`.

## 📋 Endpoints principais (resumo)

Todos os endpoints ficam sob o prefixo `/api`.

- Auth
  - POST /api/auth/register/ — Registrar usuário
  - POST /api/auth/login/ — Login (retorna token JWT)
  - POST /api/auth/logout/ — Logout (token)
  - GET/PUT /api/auth/profile/ — Perfil do usuário

- Categories
  - GET /api/categories/ — listar
  - POST /api/categories/ — criar
  - PUT /api/categories/{id}/ — atualizar
  - DELETE /api/categories/{id}/ — remover

- Expenses (lançamentos)
  - GET /api/expenses/ — listar (filtros: month, year, start_date, end_date, type, category_id)
  - POST /api/expenses/ — criar
  - PUT /api/expenses/{id}/ — atualizar
  - DELETE /api/expenses/{id}/ — remover

- Fixed Expenses (despesas fixas)
  - GET /api/fixed-expenses/ — listar
  - POST /api/fixed-expenses/ — criar
  - PUT /api/fixed-expenses/{id}/ — atualizar
  - DELETE /api/fixed-expenses/{id}/ — remover
  - POST /api/fixed-expenses/process-monthly/ — processa e cria despesas do mês

- Income (configuração de receitas)
  - GET /api/income/ — obter configuração
  - PUT /api/income/ — atualizar
  - /api/income/variable/ — CRUD para receitas variáveis
  - /api/income/fixed/ — CRUD para receitas fixas

- Reports
  - GET /api/reports/generate/ — gera relatório (JSON)
    - params: type (mensal, anual, categoria), month, year, category_id, start_date, end_date
  - GET /api/reports/pdf/ — retorna PDF (attachment)
  - POST /api/reports/email/ — envia relatório por e-mail (exige SMTP configurado)

- Analytics & Dashboard
  - GET /api/analytics/summary/ — resumo do mês
  - GET /api/analytics/chart-data/ — dados para gráficos (entradas/saidas/categorias)
  - GET /api/dashboard/stats/ — estatísticas principais
  - GET /api/dashboard/recent-transactions/ — últimas transações
  - GET /api/dashboard/all-transactions/ — todas as transações

## 📦 Exemplos rápidos (curl)

Registrar usuário:

```bash
curl -X POST "http://127.0.0.1:8000/api/auth/register/" \
  -H "Content-Type: application/json" \
  -d '{"name":"João","email":"joao@example.com","password":"senha123"}'
```

Login e pegar token (Bearer):

```bash
curl -X POST "http://127.0.0.1:8000/api/auth/login/" -H "Content-Type: application/json" -d '{"email":"joao@example.com", "password":"senha123"}'
```

Criar despesa (exemplo):

```bash
curl -X POST "http://127.0.0.1:8000/api/expenses/" \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"description":"Supermercado","amount":120.50,"category_id":1,"date":"2025-11-14","type":"despesa"}'
```

## 🧪 Testes

Não há testes automatizados detectados no repositório. Se desejar, posso adicionar uma suíte de testes (pytest + asyncio) cobrindo endpoints e serviços.

## 🤝 Contribuição

1. Fork e branch
2. Abra PR com descrição e testes

## 📄 Licença

Adicione a sua licença preferida (ex: MIT) — não encontrei arquivo `LICENSE` no repositório.

---

Se quiser, posso:

- Adicionar exemplos mais completos de payload nas seções de endpoints
- Incluir um arquivo `.env.example` com variáveis de ambiente
- Criar testes básicos para endpoints e serviços

Diga o que prefere que eu faça a seguir.