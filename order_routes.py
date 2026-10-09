from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from dependencies import pegar_sessao, verificar_token
from schemas import PedidoSchema, ItemPedidoSchema, ResponsePedidoSchema
from models import Pedido, Usuario, ItemPedido
from typing import List

order_router = APIRouter(prefix="/pedidos", tags=["pedidos"], dependencies=[Depends(verificar_token)])

@order_router.get("/")                     # FastAPI = sempre uma função "async"    /  Para criar uma rota, começar com @ e definir seu tipo (get, post...)
async def pedidos():
    """
    Essa é a rota padrão de pedidos                                 
    """                                                 # Essas """ são para fazer comentários na sua FastAPI e deixar mais didático para terceiros
    return{"mensagem": "Você acessou a rota de pedidos"}

@order_router.post("/pedidos")
async def criar_pedido(pedido_schema: PedidoSchema, session: Session = Depends(pegar_sessao)):
    """
    Cria um novo pedido.

    - **usuario**: id do usuário dono do pedido

    Retorna o id do pedido criado.
    """
    novo_pedido = Pedido(usuario=pedido_schema.usuario)
    session.add(novo_pedido)
    session.commit()
    return{"mensagem": f"Pedido criado com sucesso. Id do pedido: {novo_pedido.id}"}

@order_router.post("/pedido/cancelar/{id_pedido}")
async def cancelar_pedido(id_pedido: int, session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    """
    Cancela um pedido existente (status vira CANCELADO).

    - **id_pedido**: id do pedido a ser cancelado
    - Requer token de autenticação
    - Só o dono do pedido ou um administrador pode cancelar

    Erros: pedido não encontrado ou usuário sem autorização.
    """

    # usuario.admin = True
    # usuario.id = pedido.usuario
    pedido = session.query(Pedido).filter(Pedido.id==id_pedido).first()
    if not pedido:
        raise HTTPException(status_code=400, detail="Pedido não encontrado")            # estrutura para chamar um erro
    if not usuario.admin and usuario.id != pedido.usuario:                              # para selecionar quem vai ter acesso a cancelar o pedido
        raise HTTPException(status_code=401, detail="Você não tem autorização para fazer essa modificação")
    pedido.status = "CANCELADO"         # sempre em letras maiúsculas
    session.commit()                    # para "salvar" / encerrar sessão do bd
    return {
        "mensagem": f"Pedido número: {pedido.id} cancelado com sucesso",
        "pedido": pedido 
    }

@order_router.get("/listar")
async def listar_pedidos(session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    """
    Lista todos os pedidos do sistema.

    - Requer token de autenticação
    - Acesso restrito a administradores

    Erro: usuário sem autorização (não é admin).
    """
    if not usuario.admin:
        raise HTTPException(status_code=401, detail="Você não tem autorização para fazer essa operação")
    else:
        pedidos = session.query(Pedido).all()
        return {
            "pedidos": pedidos
        }

@order_router.post("/pedido/adicionar-item/{id_pedido}")
async def adicionar_item_pedido(id_pedido: int,
                                item_pedido_schema: ItemPedidoSchema,
                                session: Session = Depends(pegar_sessao),
                                usuario: Usuario = Depends(verificar_token)):
    """
    Adiciona um item a um pedido e recalcula o preço total.

    - **id_pedido**: id do pedido que receberá o item
    - **quantidade, sabor, tamanho, preco_unitario**: dados do item
    - Requer token de autenticação
    - Só o dono do pedido ou um administrador pode adicionar itens

    Retorna o id do item criado.
    """
    pedido = session.query(Pedido).filter(Pedido.id==id_pedido).first()
    if not pedido:
        raise HTTPException(status_code=400, detail="Pedido não existente")
    if not usuario.admin and usuario.id != pedido.usuario:
        raise HTTPException(status_code=401, detail="Você não tem autorização para fazer essa operação")
    item_pedido = ItemPedido(item_pedido_schema.quantidade, item_pedido_schema.sabor, item_pedido_schema.tamanho,
                             item_pedido_schema.preco_unitario, id_pedido)
    session.add(item_pedido)
    pedido.calcular_preco()
    session.commit()
    return{
        "mensagem": "Item criado com sucesso",
        "item_id": item_pedido.id,
        "preco_pedido": pedido
    }

@order_router.post("/pedido/remover-item/{id_pedido}")
async def remover_item_pedido(id_item_pedido: int,
                                session: Session = Depends(pegar_sessao),
                                usuario: Usuario = Depends(verificar_token)):
    """
    Remove um item de um pedido e recalcula o preço total.

    - **id_item_pedido**: id do item a ser removido
    - Requer token de autenticação
    - Só o dono do pedido ou um administrador pode remover itens

    Retorna a quantidade de itens que restaram no pedido.
    """

    item_pedido = session.query(ItemPedido).filter(ItemPedido.id==id_item_pedido).first()
    pedido = session.query(Pedido).filter(Pedido.id==item_pedido.pedido).first()
    if not item_pedido:
        raise HTTPException(status_code=400, detail="Item não existente")
    if not usuario.admin and usuario.id != pedido.usuario:              # pedido = dono do item pedido / usuario = dono do pedido
        raise HTTPException(status_code=401, detail="Você não tem autorização para fazer essa operação")
    session.delete(item_pedido)
    pedido.calcular_preco()
    session.commit()
    return{
        "mensagem": "Item removido com sucesso",
        "quantidade_itens_pedido": len(pedido.itens),       # lazy loading    /   len: para listar
        "pedido": pedido
    }

# finalizar um pedido
@order_router.post("/pedido/finalizar/{id_pedido}")
async def finalizar_pedido(id_pedido: int, session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    """
    Finaliza um pedido (status vira FINALIZADO).

    - **id_pedido**: id do pedido a ser finalizado
    - Requer token de autenticação
    - Só o dono do pedido ou um administrador pode finalizar

    Erros: pedido não encontrado ou usuário sem autorização.
    """

    pedido = session.query(Pedido).filter(Pedido.id==id_pedido).first()
    if not pedido:
            raise HTTPException(status_code=400, detail="Pedido não existente")
    if not usuario.admin and usuario.id != pedido.usuario:
            raise HTTPException(status_code=401, detail="Você não tem autorização para fazer essa modificação")
    pedido.status = "FINALIZADO"
    session.commit()
    return{
        "mensagem": f"Pedido número: {pedido.id} finalizado com sucesso",        
        "pedido": pedido
    }

# visualizar 1 pedido
@order_router.get("/pedido/{id_pedido}")
async def visualizar_pedido(id_pedido: int, session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    """
    Mostra os detalhes de um pedido.

    - **id_pedido**: id do pedido a ser visualizado
    - Requer token de autenticação
    - Só o dono do pedido ou um administrador pode visualizar

    Retorna o pedido e a quantidade de itens que ele possui.
    """

    pedido = session.query(Pedido).filter(Pedido.id==id_pedido).first()
    if not pedido:
        raise HTTPException(status_code=400, detail="Pedido não existente")
    if not usuario.admin and usuario.id != pedido.usuario:
        raise HTTPException(status_code=401, detail="Você não tem autorização para fazer essa modificação")
    return{
        "quantidade_itens_pedido" : len(pedido.itens),
        "pedido": pedido
    }
    

# visualizar todos os pedidos de 1 usuário
@order_router.get("/listar/pedidos-usuario", response_model=List[ResponsePedidoSchema])           # response_model: para conseguir enviar respostar por schema
async def listar_pedidos(session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    """
    Lista todos os pedidos do usuário logado.

    - Requer token de autenticação
    - Retorna apenas os pedidos do próprio usuário, com seus itens
    """

    pedidos = session.query(Pedido).filter(Pedido.usuario==usuario.id).all()
    return pedidos