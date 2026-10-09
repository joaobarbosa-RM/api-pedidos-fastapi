# API de Pedidos (FastAPI)

API REST para gerenciamento de pedidos, com cadastro de usuários e autenticação via JWT. Projeto de estudo desenvolvido com FastAPI, SQLAlchemy e Alembic.

## Funcionalidades

- Cadastro de usuários com senha criptografada (bcrypt)
- Login com geração de **access token** e **refresh token** (JWT)
- Criação, visualização, cancelamento e finalização de pedidos
- Adição e remoção de itens, com cálculo automático do preço total
- Controle de acesso: o usuário só acessa os próprios pedidos; administradores acessam todos
- Documentação interativa gerada automaticamente (Swagger)

## Tecnologias

- [FastAPI](https://fastapi.tiangolo.com/)
- [SQLAlchemy](https://www.sqlalchemy.org/) (ORM) com SQLite
- [Alembic](https://alembic.sqlalchemy.org/) (migrações do banco)
- [Pydantic](https://docs.pydantic.dev/) (validação de dados)
- [python-jose](https://github.com/mpdavis/python-jose) (JWT)
- [Passlib](https://passlib.readthedocs.io/) + bcrypt (hash de senhas)

## Estrutura do projeto

```
├── alembic/              # migrações do banco de dados
├── alembic.ini
├── main.py               # criação do app e configurações de segurança
├── models.py             # tabelas do banco (Usuario, Pedido, ItemPedido)
├── schemas.py            # schemas Pydantic (entrada e saída da API)
├── dependencies.py       # sessão do banco e verificação do token
├── auth_routes.py        # rotas de autenticação
├── order_routes.py       # rotas de pedidos
├── requirements.txt
└── .env.example          # modelo das variáveis de ambiente
```

## Como rodar o projeto

### 1. Clone o repositório

```bash
git clone https://github.com/joaobarbosa-RM/api-pedidos-fastapi.git
cd api-pedidos-fastapi
```

### 2. Crie e ative o ambiente virtual

**Windows (PowerShell):**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**Mac/Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Configure as variáveis de ambiente

Copie o arquivo `.env.example` para `.env`:

**Windows (PowerShell):**
```powershell
Copy-Item .env.example .env
```

**Mac/Linux:**
```bash
cp .env.example .env
```

Abra o `.env` e preencha a `SECRET_KEY`. Para gerar uma chave segura:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Exemplo de `.env` preenchido:

```
SECRET_KEY=cole-aqui-a-chave-gerada
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 5. Crie o banco de dados

```bash
alembic upgrade head
```

Isso cria o arquivo `banco.db` com todas as tabelas.

### 6. Inicie o servidor

```bash
uvicorn main:app --reload
```

A API fica disponível em `http://127.0.0.1:8000`.

## Documentação interativa

Com o servidor rodando, acesse:

- **Swagger UI:** http://127.0.0.1:8000/docs
- **ReDoc:** http://127.0.0.1:8000/redoc

Para testar as rotas protegidas pelo Swagger, clique em **Authorize** e faça login com o e-mail (no campo `username`) e a senha cadastrados.

## Principais rotas

### Autenticação (`/auth`)

| Método | Rota | Descrição |
|--------|------|-----------|
| POST | `/auth/criar_conta` | Cria um novo usuário |
| POST | `/auth/login` | Login com JSON, retorna access e refresh token |
| POST | `/auth/login-form` | Login via formulário (usado pelo botão Authorize do Swagger) |
| GET | `/auth/refresh` | Gera um novo access token |

### Pedidos (`/pedidos`)

Todas as rotas de pedidos exigem token de autenticação.

| Método | Rota | Descrição |
|--------|------|-----------|
| POST | `/pedidos/pedidos` | Cria um pedido |
| GET | `/pedidos/pedido/{id_pedido}` | Visualiza um pedido |
| POST | `/pedidos/pedido/cancelar/{id_pedido}` | Cancela um pedido |
| POST | `/pedidos/pedido/finalizar/{id_pedido}` | Finaliza um pedido |
| POST | `/pedidos/pedido/adicionar-item/{id_pedido}` | Adiciona um item ao pedido |
| POST | `/pedidos/pedido/remover-item/{id_item_pedido}` | Remove um item do pedido |
| GET | `/pedidos/listar` | Lista todos os pedidos (apenas admin) |
| GET | `/pedidos/listar/pedidos-usuario` | Lista os pedidos do usuário logado |

## Exemplo de uso

**1. Criar uma conta**

```bash
curl -X POST "http://127.0.0.1:8000/auth/criar_conta" \
  -H "Content-Type: application/json" \
  -d '{"nome": "Maria", "email": "maria@email.com", "senha": "123456"}'
```

**2. Fazer login**

```bash
curl -X POST "http://127.0.0.1:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "maria@email.com", "senha": "123456"}'
```

**3. Usar o token em uma rota protegida**

```bash
curl "http://127.0.0.1:8000/pedidos/listar/pedidos-usuario" \
  -H "Authorization: Bearer SEU_ACCESS_TOKEN"
```

## Migrações do banco

Sempre que alterar os models em `models.py`:

```bash
alembic revision --autogenerate -m "descrição da alteração"
alembic upgrade head
```

## Observações

Este é um projeto de estudo. Para uso em produção, seria necessário, entre outros pontos: usar um banco como PostgreSQL, diferenciar access token e refresh token, restringir origens (CORS) e guardar os segredos em um serviço próprio de gerenciamento de variáveis.

## Autor

**João Vitor Barbosa**