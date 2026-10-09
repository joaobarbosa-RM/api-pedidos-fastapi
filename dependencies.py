from fastapi import Depends, HTTPException
from main import SECRET_KEY, ALGORITHM, oauth2_schema
from models import db   # para importar uma tabela do banco de dados
from sqlalchemy.orm import sessionmaker, Session    # para criar uma sessão no banco de dados
from models import Usuario
from jose import jwt, JWTError



def pegar_sessao():                              # dependencia = função para criar uma sessão direto no banco de dados, sem precisar criar várias separadas
    try:                                         # try: tentar rodar
        Session = sessionmaker(bind=db)
        session = Session()
        yield session                               # yield: faz o retorno da função mas não encerra ela
    finally:                                        # finally: independente do que aconteça (der errado ou certo), rodar o código todo
        session.close()                           


def verificar_token(token: str = Depends(oauth2_schema), session: Session = Depends(pegar_sessao)):           # função para retornar qual usuário é dono do token
    try:
        dic_info = jwt.decode(token, SECRET_KEY, ALGORITHM)                     # decode: para verificar o token (decodificar)
        id_usuario = int(dic_info.get("sub"))
    except JWTError:
        raise HTTPException(status_code=401, detail="Acesso negado, verifique a validade do token")
    # verificar se o token é válido
    # extrair o ID do usuário do token
    usuario = session.query(Usuario).filter(Usuario.id==id_usuario).first()
    if not usuario:
        raise HTTPException(status_code=401, detail="Acesso Inválido")
    return usuario