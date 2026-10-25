"""Modelos ORM: cada classe é mapeada para uma tabela do banco."""
from datetime import date, datetime, timezone
from typing import Optional

from sqlalchemy import Date, DateTime, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


def agora() -> datetime:
    return datetime.now(timezone.utc)


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    senha_hash: Mapped[str] = mapped_column(String(255))
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=agora)

    categorias: Mapped[list["Categoria"]] = relationship(
        back_populates="dono", cascade="all, delete-orphan"
    )
    tarefas: Mapped[list["Tarefa"]] = relationship(
        back_populates="dono", cascade="all, delete-orphan"
    )


class Categoria(Base):
    __tablename__ = "categorias"
    __table_args__ = (
        UniqueConstraint("usuario_id", "nome", name="uq_categoria_usuario_nome"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(80))
    descricao: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), index=True)

    dono: Mapped["Usuario"] = relationship(back_populates="categorias")
    tarefas: Mapped[list["Tarefa"]] = relationship(back_populates="categoria")


class Tarefa(Base):
    __tablename__ = "tarefas"

    id: Mapped[int] = mapped_column(primary_key=True)
    titulo: Mapped[str] = mapped_column(String(120))
    descricao: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="pendente", index=True)
    prioridade: Mapped[str] = mapped_column(String(10), default="media")
    prazo: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=agora)
    atualizado_em: Mapped[datetime] = mapped_column(DateTime, default=agora, onupdate=agora)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), index=True)
    categoria_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("categorias.id"), nullable=True, index=True
    )

    dono: Mapped["Usuario"] = relationship(back_populates="tarefas")
    categoria: Mapped[Optional["Categoria"]] = relationship(back_populates="tarefas")
