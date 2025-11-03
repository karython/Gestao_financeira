# Rotas do Backend FastAPI - Sistema de Gestão Financeira Pessoal

## Autenticação

### POST /api/auth/register/
- Cadastro de novo usuário
- Dados: name, email, password

### POST /api/auth/login/
- Login de usuário
- Dados: email, password
- Retorna: token de autenticação

### POST /api/auth/logout/
- Logout do usuário
- Header: Authorization: Bearer {token}

### GET /api/auth/profile/
- Retorna dados do usuário autenticado
- Header: Authorization: Bearer {token}

### PUT /api/auth/profile/
- Atualiza dados do usuário
- Header: Authorization: Bearer {token}
- Dados: name, email, password (opcional)

## Categorias

### GET /api/categories/
- Lista todas as categorias do usuário
- Header: Authorization: Bearer {token}

### POST /api/categories/
- Cria nova categoria
- Header: Authorization: Bearer {token}
- Dados: name, type (despesa/receita)

### PUT /api/categories/{id}/
- Atualiza categoria
- Header: Authorization: Bearer {token}
- Dados: name, type

### DELETE /api/categories/{id}/
- Remove categoria
- Header: Authorization: Bearer {token}

## Lançamentos (Despesas/Receitas)

### GET /api/expenses/
- Lista todos os lançamentos
- Header: Authorization: Bearer {token}
- Query params: ?month=10&year=2025&type=despesa&category_id=1

### POST /api/expenses/
- Cria novo lançamento
- Header: Authorization: Bearer {token}
- Dados: description, amount, category_id, date, type

### PUT /api/expenses/{id}/
- Atualiza lançamento
- Header: Authorization: Bearer {token}
- Dados: description, amount, category_id, date, type

### DELETE /api/expenses/{id}/
- Remove lançamento
- Header: Authorization: Bearer {token}

## Despesas Fixas

### GET /api/fixed-expenses/
- Lista todas as despesas fixas
- Header: Authorization: Bearer {token}

### POST /api/fixed-expenses/
- Cria nova despesa fixa
- Header: Authorization: Bearer {token}
- Dados: description, amount, category_id, day_of_month

### PUT /api/fixed-expenses/{id}/
- Atualiza despesa fixa
- Header: Authorization: Bearer {token}
- Dados: description, amount, category_id, day_of_month

### DELETE /api/fixed-expenses/{id}/
- Remove despesa fixa
- Header: Authorization: Bearer {token}

### POST /api/fixed-expenses/process-monthly/
- Processa despesas fixas do mês (cria lançamentos automáticos)
- Header: Authorization: Bearer {token}

## Receitas

### GET /api/income/
- Retorna configuração de receitas do usuário
- Header: Authorization: Bearer {token}

### PUT /api/income/
- Atualiza configuração de receitas
- Header: Authorization: Bearer {token}
- Dados: fixed, bonus

### GET /api/income/variable/
- Lista receitas variáveis
- Header: Authorization: Bearer {token}

### POST /api/income/variable/
- Adiciona receita variável
- Header: Authorization: Bearer {token}
- Dados: description, amount, valid_until

### PUT /api/income/variable/{id}/
- Atualiza receita variável
- Header: Authorization: Bearer {token}
- Dados: description, amount, valid_until

### DELETE /api/income/variable/{id}/
- Remove receita variável
- Header: Authorization: Bearer {token}

## Relatórios

### GET /api/reports/generate/
- Gera relatório
- Header: Authorization: Bearer {token}
- Query params: ?type=mensal&category_id=1&month=10&year=2025

### GET /api/reports/pdf/
- Gera PDF do relatório
- Header: Authorization: Bearer {token}
- Query params: ?type=mensal&category_id=1&month=10&year=2025
- Retorna: arquivo PDF

### POST /api/reports/email/
- Envia relatório por email
- Header: Authorization: Bearer {token}
- Dados: type, category_id, month, year, email

## Análises/Dashboard

### GET /api/analytics/summary/
- Retorna resumo financeiro
- Header: Authorization: Bearer {token}
- Query params: ?month=10&year=2025

### GET /api/analytics/chart-data/
- Retorna dados para gráficos
- Header: Authorization: Bearer {token}
- Query params: ?filter=entradas&period=mensal&month=10&year=2025

### GET /api/dashboard/stats/
- Retorna estatísticas do dashboard
- Header: Authorization: Bearer {token}

### GET /api/dashboard/recent-transactions/
- Retorna transações recentes
- Header: Authorization: Bearer {token}
- Query params: ?limit=10

## Modelos Django Necessários

### User (customizado)
```python
- id
- name
- email
- password
- avatar
- created_at
- updated_at
```

### Category
```python
- id
- user (ForeignKey)
- name
- type (choices: despesa/receita)
- created_at
- updated_at
```

### Expense
```python
- id
- user (ForeignKey)
- description
- amount
- category (ForeignKey)
- date
- type (choices: despesa/receita)
- created_at
- updated_at
```

### FixedExpense
```python
- id
- user (ForeignKey)
- description
- amount
- category (ForeignKey)
- day_of_month
- is_active
- created_at
- updated_at
```

### Income
```python
- id
- user (OneToOneField)
- fixed_amount
- bonus_amount
- created_at
- updated_at
```

### VariableIncome
```python
- id
- income (ForeignKey)
- description
- amount
- valid_until
- is_active
- created_at
- updated_at
```

## Configurações CORS

Adicionar no settings.py:
```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8000",
]

CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]
```

## Autenticação JWT

Usar Django Rest Framework com Simple JWT:
```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}
```

## Observações Importantes

1. Todas as rotas (exceto login e register) devem validar o token JWT
2. Cada usuário só pode acessar seus próprios dados
3. Implementar paginação para listas grandes
4. Adicionar validações de dados no serializer
5. Implementar cache para otimizar consultas frequentes
6. Adicionar logs para auditoria
7. Implementar rate limiting para prevenir abuso
8. Usar transações para operações críticas
9. Adicionar testes unitários para cada endpoint
10. Documentar API com Swagger/OpenAPI
