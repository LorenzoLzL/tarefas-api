# API de Tarefas e Categorias

API REST para gerenciar **tarefas** organizadas em **categorias**, com cadastro/login de usuários e autenticação por **JWT**. Cada usuário enxerga e altera somente os próprios dados.

Trabalho final de *Arquitetura e Desenvolvimento de APIs* (Uninter).

## Problema resolvido

Pessoas que organizam estudos e afazeres precisam de um serviço central, acessível por qualquer cliente (web, mobile, scripts), para registrar tarefas, classificá-las por categoria, prioridade e status, e consultá-las com filtros. Esta API oferece essa base.

## Tecnologias

| Item | Tecnologia |
|---|---|
| Linguagem | Python 3.10+ |
| Framework | FastAPI (+ Uvicorn) |
| Banco de dados | SQLite (arquivo local `tarefas.db`) |
| ORM | SQLAlchemy 2.0 |
| Validação | Pydantic v2 |
| Autenticação | JWT (PyJWT) + hash de senha PBKDF2-SHA256 |
| Documentação | Swagger UI / OpenAPI (gerado automaticamente) |
| Testes | pytest + TestClient (httpx) |

## Pré-requisitos

- Python 3.10 ou superior
- `pip` e (recomendado) `venv`
- Git

## Instalação

```bash
git clone <URL-DO-REPOSITORIO>
cd tarefas-api

python -m venv .venv
# Linux/macOS:
source .venv/bin/activate
# Windows (PowerShell):
.venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

## Configuração (variáveis de ambiente)

```bash
cp .env.example .env        # Windows: copy .env.example .env
```

Edite o `.env` e defina ao menos a `SECRET_KEY`. Para gerar uma chave:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

| Variável | Descrição | Padrão |
|---|---|---|
| `SECRET_KEY` | Chave de assinatura do JWT (**obrigatória**) | — |
| `DATABASE_URL` | URL do banco | `sqlite:///./tarefas.db` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Validade do token | `60` |
| `CORS_ORIGINS` | Origens permitidas, separadas por vírgula | `http://localhost:3000,http://localhost:5173` |

### Banco de dados

Não é preciso criar nada manualmente: as tabelas são criadas automaticamente na primeira execução (via ORM). Se preferir criar pelo script SQL:

```bash
sqlite3 tarefas.db < schema.sql
```

## Executando a API

```bash
uvicorn app.main:app --reload
```

- API: http://127.0.0.1:8000
- **Swagger UI:** http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc
- OpenAPI (JSON): http://127.0.0.1:8000/openapi.json

## Executando os testes automatizados

```bash
pytest -v
```

Os testes usam um banco SQLite em memória e não alteram o `tarefas.db`.

## Resumo dos endpoints

| Método | Endpoint | Descrição | Auth | Respostas |
|---|---|---|---|---|
| POST | `/auth/register` | Cadastrar usuário | Não | 201 / 400 / 409 |
| POST | `/auth/login` | Obter token JWT | Não | 200 / 400 / 401 |
| GET | `/auth/me` | Dados do usuário logado | Sim | 200 / 401 |
| GET | `/categorias` | Listar categorias | Sim | 200 / 401 |
| GET | `/categorias/{id}` | Consultar categoria | Sim | 200 / 401 / 404 |
| POST | `/categorias` | Criar categoria | Sim | 201 / 400 / 401 / 409 |
| PATCH | `/categorias/{id}` | Atualizar categoria | Sim | 200 / 400 / 401 / 404 / 409 |
| DELETE | `/categorias/{id}` | Excluir categoria | Sim | 204 / 401 / 404 / 409 |
| GET | `/tarefas` | Listar tarefas (filtros e paginação) | Sim | 200 / 400 / 401 |
| GET | `/tarefas/{id}` | Consultar tarefa | Sim | 200 / 401 / 404 |
| POST | `/tarefas` | Criar tarefa | Sim | 201 / 400 / 401 |
| PATCH | `/tarefas/{id}` | Atualizar parcialmente | Sim | 200 / 400 / 401 / 404 |
| DELETE | `/tarefas/{id}` | Excluir tarefa | Sim | 204 / 401 / 404 |

**Filtros de `GET /tarefas`:** `status` (`pendente`, `em_andamento`, `concluida`), `prioridade` (`baixa`, `media`, `alta`), `categoria_id`, `busca` (texto no título/descrição), `skip` e `limit` (máx. 100).

## Testando a autenticação (sem expor credenciais)

Crie um usuário de teste com os seus próprios dados — nenhuma credencial fica no repositório.

**1. Cadastrar**

```bash
curl -X POST http://127.0.0.1:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"nome":"Maria Silva","email":"maria@exemplo.com","senha":"senhaSegura123"}'
```

**2. Fazer login e copiar o `access_token`**

```bash
curl -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"maria@exemplo.com","senha":"senhaSegura123"}'
```

**3. Usar o token nas rotas protegidas**

```bash
TOKEN="cole_o_token_aqui"

# Criar categoria
curl -X POST http://127.0.0.1:8000/categorias \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"nome":"Estudos","descricao":"Atividades da faculdade"}'

# Criar tarefa
curl -X POST http://127.0.0.1:8000/tarefas \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"titulo":"Entregar trabalho de APIs","prioridade":"alta","prazo":"2026-11-30","categoria_id":1}'

# Listar com filtros
curl "http://127.0.0.1:8000/tarefas?status=pendente&prioridade=alta" -H "Authorization: Bearer $TOKEN"

# Atualizar parcialmente
curl -X PATCH http://127.0.0.1:8000/tarefas/1 \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"status":"concluida"}'

# Excluir
curl -X DELETE http://127.0.0.1:8000/tarefas/1 -H "Authorization: Bearer $TOKEN"

# Sem token => 401
curl -i http://127.0.0.1:8000/tarefas
```

**No Swagger:** faça o login em `POST /auth/login`, copie o `access_token`, clique em **Authorize** (cadeado) e cole **apenas o token**.

## Estrutura do projeto

```
tarefas-api/
├── app/
│   ├── main.py          # criação do app, CORS, tratamento de erros de validação
│   ├── config.py        # leitura das variáveis de ambiente
│   ├── database.py      # engine, sessão e Base do SQLAlchemy
│   ├── models.py        # modelos ORM (Usuario, Categoria, Tarefa)
│   ├── schemas.py       # schemas Pydantic (validação e saída)
│   ├── security.py      # hash de senha e JWT
│   ├── deps.py          # dependência de autenticação (usuario_atual)
│   └── routers/         # auth.py, categorias.py, tarefas.py
├── tests/               # testes automatizados (pytest)
├── docs/evidencias/     # capturas de tela e saídas dos testes
├── schema.sql           # script de criação do banco
├── requirements.txt
├── .env.example
└── README.md
```

## Decisões de projeto

- **PATCH em vez de PUT:** o cliente envia só os campos que mudam (ex.: apenas `status`), evitando reenviar o recurso inteiro.
- **CORS restritivo:** somente origens da lista `CORS_ORIGINS`, métodos `GET/POST/PATCH/DELETE/OPTIONS` e cabeçalhos `Authorization`/`Content-Type`; sem cookies (`allow_credentials=False`), pois a autenticação usa o cabeçalho `Authorization`.
- **404 para recurso de outro usuário:** evita revelar a existência de registros alheios.
- **400 para dados inválidos:** os erros de validação do Pydantic são convertidos em respostas `400` com a lista de campos e mensagens.
