from fastapi import FastAPI
from passlib.context import CryptContext                  # Para criptografar senhas, etc
from fastapi.security import OAuth2PasswordBearer         # Para criar a estrutura bearer e passar as informações pela header
from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")                    # Para buscar a secrete key no arquivo .env
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

app = FastAPI()    # Criar o app

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")           # schemes = esquemas de criptografia
oauth2_schema = OAuth2PasswordBearer(tokenUrl="auth/login-form")


from auth_routes import auth_router
from order_routes import order_router

app.include_router(auth_router)         # Para incluir as rotas no app
app.include_router(order_router)



# Para rodar o código, executar no terminal: uvicorn main:app --reload   

#RestAPI:
# Get -> leitura/pegar
# Post -> enviar/criar
# Put/Patch -> edição
# Delete -> deletar
# endpoint -> link (ex: /ordens)