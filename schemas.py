from pydantic import BaseModel          # pydantic: força você a definir os tipos de dados
from typing import Optional, List             # para importar os tipos de dados


#classe para passar parametros com schemas
class UsuarioSchema(BaseModel):
    nome: str
    email: str
    senha: str
    ativo: Optional[bool]
    admin: Optional[bool]

    class Config:                       # classe para fazer a conexão com a pasta models.py
        from_attributes = True


class PedidoSchema(BaseModel):
    usuario: int

    class Config:
        from_attributes = True

class LoginSchema(BaseModel):
    email: str
    senha: str

    class Config:
        from_attributes = True

class ItemPedidoSchema(BaseModel):
    quantidade: int
    sabor: str
    tamanho: str
    preco_unitario: float

    class Config:
        from_attributes = True

class ResponsePedidoSchema(BaseModel):
    id: int
    status: str
    preco: float
    itens: List[ItemPedidoSchema]

    class Config:
        from_attributes = True
    