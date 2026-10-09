from sqlalchemy import create_engine, Column, String, Integer, Boolean, Float, ForeignKey
from sqlalchemy.orm import declarative_base, relationship      # relationship = para conectar as tabelas
from sqlalchemy_utils.types import ChoiceType

# cria a conexão com seu banco de dados
db = create_engine("sqlite:///banco.db")

# cria a base do banco de dados                   "Base" faz a tradução das classes para tabelas
Base = declarative_base()

# cria as classes/tabelas do banco
class Usuario(Base):
    __tablename__ = "usuarios"               

    id = Column("id", Integer, primary_key=True, autoincrement=True)              # colunas do banco      autoincrement: conta a quantidade de usuarios automaticamente
    nome = Column("nome", String)
    email = Column("email", String, nullable=False)                               # nullable: não deixa você criar um usuario sem email
    senha = Column("senha", String)
    ativo = Column("ativo", Boolean)
    admin = Column ("admin", Boolean, default=False)

    def __init__(self, nome, email, senha, ativo=True, admin=False):                         # Função para declarar oque você quer fazer quando criar um usuário
        self.nome = nome
        self.email = email
        self.senha = senha
        self.ativo = ativo
        self.admin = admin


class Pedido(Base):
    __tablename__ = "pedidos"

    #STATUS_PEDIDOS = (
        #("CHAVE", "VALOR")       CHAVE: vai para o banco de dados  /  VALOR: é visível
        #("PENDENTE", "PENDENTE"),
        #("CANCELADO", "CANCELADO"),
        #("FINALIZADO", "FINALIZADO"),
     #)
    id = Column("id", Integer, primary_key=True, autoincrement=True)
    status = Column("status", String)
    usuario = Column("usuario", ForeignKey("usuarios.id"))                       # ForeingKey: para buscar valores de outras tabelas
    preco = Column("preco", Float)
    itens = relationship("ItemPedido", cascade="all, delete")                    # cascade: para cascadiar e deletar todos os itens relacionados a um pedido especifico

    def __init__(self, usuario, status="PENDENTE", preco=0):
        self.usuario = usuario
        self.preco = preco
        self.status = status

    def calcular_preco(self):
        # percorrer todos os itens do pedido
        # somar todos os precos de todos os itens dos pedidos
        # editar no campo "preco" o valor final do preco do pedido
        self.preco = sum(item.preco_unitario * item.quantidade for item in self.itens)

class ItemPedido(Base):
    __tablename__ = "itens_pedidos"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    quantidade = Column("quantidade", Integer)
    sabor = Column("sabor", String)
    tamanho = Column("tamanho", String)
    preco_unitario = Column("preco_unitario", Float)
    pedido = Column("pedido", ForeignKey("pedidos.id"))

    def __init__(self, quantidade, sabor, tamanho, preco_unitario, pedido):
        self.quantidade = quantidade
        self.sabor = sabor
        self.tamanho = tamanho
        self.preco_unitario = preco_unitario
        self.pedido = pedido





# alembic revision --autogenerate -m "adicionar itens no Pedido"
# alembic upgrade head