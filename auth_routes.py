from fastapi import APIRouter, Depends, HTTPException                               # Router = roteador de rota  /   Depends = função para ligar a variável da pasta dependencies.py
from models import Usuario                               # para importar uma tabela do banco de dados
from dependencies import pegar_sessao, verificar_token
from main import bcrypt_context, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY
from schemas import UsuarioSchema, LoginSchema
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
from fastapi.security import OAuth2PasswordRequestForm


auth_router = APIRouter(prefix="/auth", tags=["auth"])     # sempre definir um prefixo


def criar_token(id_usuario, duracao_token=timedelta(ACCESS_TOKEN_EXPIRE_MINUTES)):
    data_expiracao = datetime.now(timezone.utc) + duracao_token           # para definir o tempo de expiração do token
    dic_info = {"sub": str(id_usuario), "exp": data_expiracao}           # dicionário do token
    jwt_codificado = jwt.encode(dic_info, SECRET_KEY, ALGORITHM)                # parametros necessarios para a geração do jwt token
    return jwt_codificado


def autenticar_usuario(email, senha, session):                            # função para verificar senha
    usuario = session.query(Usuario).filter(Usuario.email == email).first()
    if not usuario:
        return False
    elif not bcrypt_context.verify(senha, usuario.senha):                # verify: para verificar se a senha é igual a hash
        return False
    return usuario


@auth_router.get("/")
async def home():
    """
    Essa é a rota padrão de autenticação
    """
    return {"mensagem": "Você acessou a rota de autenticação", "autenticado": False}


@auth_router.post("/criar_conta")                                    # rota e função para a criação do usuário
async def criar_conta(usuario_schema: UsuarioSchema, session: Session = Depends(pegar_sessao)):            # a sessão vira parametro
    """
    Cria uma nova conta de usuário.

    - **nome, email, senha**: dados do novo usuário
    - **ativo, admin**: permissões e status da conta
    - A senha é salva criptografada (hash), nunca em texto puro

    Erro: e-mail já cadastrado.
    """

    usuario = session.query(Usuario).filter(Usuario.email == usuario_schema.email).first()             # Estrutura para criar uma sessão  /  query: para fazer buscas em tabelas
    if usuario:
        # Já existe um usuário com esse email
        raise HTTPException(status_code=400, detail="E-mail já cadastrado")             # Estrutura para mostrar erro ao usuário
    else:
        senha_criptografada = bcrypt_context.hash(usuario_schema.senha)                                   # hash = um código criptografado
        novo_usuario = Usuario(
            nome=usuario_schema.nome,
            email=usuario_schema.email,
            senha=senha_criptografada,
            ativo=usuario_schema.ativo,
            admin=usuario_schema.admin
        )                                    # dentro da parenteses estão os requisitos para criar um novo usuário
        session.add(novo_usuario)                                                     # adicionar o novo usuario na sessão
        session.commit()                                                              # commit: para salvar no banco de dados
        return {"mensagem": f"Usuário cadastrado com sucesso: {usuario_schema.email}"}


# login -> email e senha -> token JWT (Json Web Token)
@auth_router.post("/login")
async def login(login_schema: LoginSchema, session: Session = Depends(pegar_sessao)):
    """
    Faz login com e-mail e senha (dados enviados em JSON).

    - **email, senha**: credenciais do usuário

    Retorna um **access_token** (curta duração, usado nas rotas protegidas)
    e um **refresh_token** (7 dias, usado para gerar novos access tokens
    sem precisar fazer login de novo).

    Erro: usuário não encontrado ou senha incorreta.
    """

    usuario = autenticar_usuario(login_schema.email, login_schema.senha, session)
    if not usuario:
        raise HTTPException(status_code=400, detail="Usuário não encontrado")
    else:
        access_token = criar_token(usuario.id)
        refresh_token = criar_token(usuario.id, duracao_token=timedelta(days=7))                         # refresh token: para o usuario não precisar fazendo login toda hora
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer"
        }

@auth_router.post("/login-form")
async def login_form(dados_formulario: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(pegar_sessao)):
    """
    Faz login usando formulário (campos **username** e **password**).

    - **username**: o e-mail do usuário
    - **password**: a senha

    Essa rota existe para o botão **Authorize** da documentação (/docs),
    que envia os dados como formulário e não como JSON.

    Retorna um **access_token**.

    Erro: usuário não encontrado ou senha incorreta.
    """

    usuario = autenticar_usuario(dados_formulario.username, dados_formulario.password, session)
    if not usuario:
        raise HTTPException(status_code=400, detail="Usuário não encontrado")
    else:
        access_token = criar_token(usuario.id)
        return {
            "access_token": access_token,
            "token_type": "Bearer"
        }
    # JWT Bearer
    # headers = {"Access-Token": "Bearer Token"}

@auth_router.get("/refresh")
async def use_refresh_token(usuario: Usuario = Depends(verificar_token)):                   # "usuario:" porque a função verificar_token me retorna um "usuario"
    """
    Gera um novo access token a partir de um token válido.

    - Requer token de autenticação (Bearer) no cabeçalho
    - Evita que o usuário precise fazer login toda vez que o token expira

    Retorna um novo **access_token**.
    """

    access_token = criar_token(usuario.id)
    return {
        "access_token": access_token,
        "token_type": "Bearer"

    }