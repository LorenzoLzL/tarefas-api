"""CRUD de categorias. Todas as rotas exigem autenticação e são isoladas por usuário."""
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import usuario_atual
from ..models import Categoria, Tarefa, Usuario
from ..schemas import CategoriaCreate, CategoriaOut, CategoriaUpdate

router = APIRouter(prefix="/categorias", tags=["Categorias"])


def _buscar(db: Session, categoria_id: int, usuario: Usuario) -> Categoria:
    categoria = db.scalar(
        select(Categoria).where(Categoria.id == categoria_id, Categoria.usuario_id == usuario.id)
    )
    if categoria is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Categoria não encontrada.")
    return categoria


def _nome_em_uso(db: Session, nome: str, usuario: Usuario, ignorar_id: int | None = None) -> bool:
    consulta = select(Categoria.id).where(
        Categoria.usuario_id == usuario.id, func.lower(Categoria.nome) == nome.lower()
    )
    if ignorar_id is not None:
        consulta = consulta.where(Categoria.id != ignorar_id)
    return db.scalar(consulta) is not None


@router.get("", response_model=list[CategoriaOut])
def listar(db: Session = Depends(get_db), usuario: Usuario = Depends(usuario_atual)):
    consulta = select(Categoria).where(Categoria.usuario_id == usuario.id).order_by(Categoria.nome)
    return db.scalars(consulta).all()


@router.get("/{categoria_id}", response_model=CategoriaOut)
def obter(categoria_id: int, db: Session = Depends(get_db), usuario: Usuario = Depends(usuario_atual)):
    return _buscar(db, categoria_id, usuario)


@router.post("", response_model=CategoriaOut, status_code=status.HTTP_201_CREATED)
def criar(dados: CategoriaCreate, db: Session = Depends(get_db), usuario: Usuario = Depends(usuario_atual)):
    if _nome_em_uso(db, dados.nome, usuario):
        raise HTTPException(status.HTTP_409_CONFLICT, "Você já possui uma categoria com este nome.")
    categoria = Categoria(nome=dados.nome, descricao=dados.descricao, usuario_id=usuario.id)
    db.add(categoria)
    db.commit()
    db.refresh(categoria)
    return categoria


@router.patch("/{categoria_id}", response_model=CategoriaOut)
def atualizar(
    categoria_id: int,
    dados: CategoriaUpdate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(usuario_atual),
):
    categoria = _buscar(db, categoria_id, usuario)
    alteracoes = dados.model_dump(exclude_unset=True)
    novo_nome = alteracoes.get("nome")
    if novo_nome and _nome_em_uso(db, novo_nome, usuario, ignorar_id=categoria.id):
        raise HTTPException(status.HTTP_409_CONFLICT, "Você já possui uma categoria com este nome.")
    for campo, valor in alteracoes.items():
        setattr(categoria, campo, valor)
    db.commit()
    db.refresh(categoria)
    return categoria


@router.delete("/{categoria_id}", status_code=status.HTTP_204_NO_CONTENT)
def excluir(categoria_id: int, db: Session = Depends(get_db), usuario: Usuario = Depends(usuario_atual)):
    categoria = _buscar(db, categoria_id, usuario)
    if db.scalar(select(Tarefa.id).where(Tarefa.categoria_id == categoria.id).limit(1)) is not None:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            "Não é possível excluir uma categoria que possui tarefas associadas.",
        )
    db.delete(categoria)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
