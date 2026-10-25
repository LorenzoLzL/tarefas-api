"""CRUD de tarefas com filtros e paginação. Rotas protegidas e isoladas por usuário."""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import usuario_atual
from ..models import Categoria, Tarefa, Usuario
from ..schemas import Prioridade, StatusTarefa, TarefaCreate, TarefaOut, TarefaUpdate

router = APIRouter(prefix="/tarefas", tags=["Tarefas"])


def _buscar(db: Session, tarefa_id: int, usuario: Usuario) -> Tarefa:
    tarefa = db.scalar(select(Tarefa).where(Tarefa.id == tarefa_id, Tarefa.usuario_id == usuario.id))
    if tarefa is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Tarefa não encontrada.")
    return tarefa


def _validar_categoria(db: Session, categoria_id: Optional[int], usuario: Usuario) -> None:
    if categoria_id is None:
        return
    existe = db.scalar(
        select(Categoria.id).where(Categoria.id == categoria_id, Categoria.usuario_id == usuario.id)
    )
    if existe is None:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, f"A categoria {categoria_id} não existe para este usuário."
        )


@router.get("", response_model=list[TarefaOut])
def listar(
    status_tarefa: Optional[StatusTarefa] = Query(default=None, alias="status"),
    prioridade: Optional[Prioridade] = None,
    categoria_id: Optional[int] = Query(default=None, ge=1),
    busca: Optional[str] = Query(default=None, min_length=1, max_length=100,
                                 description="Texto contido no título ou na descrição"),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(usuario_atual),
):
    consulta = select(Tarefa).where(Tarefa.usuario_id == usuario.id)
    if status_tarefa:
        consulta = consulta.where(Tarefa.status == status_tarefa.value)
    if prioridade:
        consulta = consulta.where(Tarefa.prioridade == prioridade.value)
    if categoria_id:
        consulta = consulta.where(Tarefa.categoria_id == categoria_id)
    if busca:
        termo = f"%{busca}%"
        consulta = consulta.where(or_(Tarefa.titulo.ilike(termo), Tarefa.descricao.ilike(termo)))
    consulta = consulta.order_by(Tarefa.id).offset(skip).limit(limit)
    return db.scalars(consulta).all()


@router.get("/{tarefa_id}", response_model=TarefaOut)
def obter(tarefa_id: int, db: Session = Depends(get_db), usuario: Usuario = Depends(usuario_atual)):
    return _buscar(db, tarefa_id, usuario)


@router.post("", response_model=TarefaOut, status_code=status.HTTP_201_CREATED)
def criar(dados: TarefaCreate, db: Session = Depends(get_db), usuario: Usuario = Depends(usuario_atual)):
    _validar_categoria(db, dados.categoria_id, usuario)
    tarefa = Tarefa(
        titulo=dados.titulo,
        descricao=dados.descricao,
        status=dados.status.value,
        prioridade=dados.prioridade.value,
        prazo=dados.prazo,
        categoria_id=dados.categoria_id,
        usuario_id=usuario.id,
    )
    db.add(tarefa)
    db.commit()
    db.refresh(tarefa)
    return tarefa


@router.patch("/{tarefa_id}", response_model=TarefaOut)
def atualizar(
    tarefa_id: int,
    dados: TarefaUpdate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(usuario_atual),
):
    """Atualização parcial: apenas os campos enviados no corpo são alterados."""
    tarefa = _buscar(db, tarefa_id, usuario)
    alteracoes = dados.model_dump(exclude_unset=True)
    if "categoria_id" in alteracoes:
        _validar_categoria(db, alteracoes["categoria_id"], usuario)
    for campo, valor in alteracoes.items():
        # Enums viram o texto armazenado no banco
        setattr(tarefa, campo, getattr(valor, "value", valor))
    db.commit()
    db.refresh(tarefa)
    return tarefa


@router.delete("/{tarefa_id}", status_code=status.HTTP_204_NO_CONTENT)
def excluir(tarefa_id: int, db: Session = Depends(get_db), usuario: Usuario = Depends(usuario_atual)):
    tarefa = _buscar(db, tarefa_id, usuario)
    db.delete(tarefa)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
