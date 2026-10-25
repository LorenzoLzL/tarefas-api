"""Schemas Pydantic: validam a entrada e definem o formato JSON da saída."""
from datetime import date, datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class StatusTarefa(str, Enum):
    pendente = "pendente"
    em_andamento = "em_andamento"
    concluida = "concluida"


class Prioridade(str, Enum):
    baixa = "baixa"
    media = "media"
    alta = "alta"


class Base(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, from_attributes=True)


# ---------- Autenticação ----------
class UsuarioCreate(Base):
    nome: str = Field(min_length=2, max_length=100, examples=["Maria Silva"])
    email: EmailStr = Field(examples=["maria@exemplo.com"])
    senha: str = Field(min_length=8, max_length=128, examples=["senhaSegura123"])


class UsuarioOut(Base):
    id: int
    nome: str
    email: EmailStr


class LoginIn(Base):
    email: EmailStr
    senha: str = Field(min_length=1, max_length=128)


class TokenOut(Base):
    access_token: str
    token_type: str = "bearer"


# ---------- Categorias ----------
class CategoriaCreate(Base):
    nome: str = Field(min_length=1, max_length=80, examples=["Estudos"])
    descricao: Optional[str] = Field(default=None, max_length=255)


class CategoriaUpdate(Base):
    nome: Optional[str] = Field(default=None, min_length=1, max_length=80)
    descricao: Optional[str] = Field(default=None, max_length=255)

    @field_validator("nome")
    @classmethod
    def nome_nao_nulo(cls, v):
        if v is None:
            raise ValueError("O nome não pode ser nulo.")
        return v


class CategoriaOut(Base):
    id: int
    nome: str
    descricao: Optional[str] = None


# ---------- Tarefas ----------
class TarefaCreate(Base):
    titulo: str = Field(min_length=3, max_length=120, examples=["Estudar para a prova de APIs"])
    descricao: Optional[str] = Field(default=None, max_length=2000)
    status: StatusTarefa = StatusTarefa.pendente
    prioridade: Prioridade = Prioridade.media
    prazo: Optional[date] = None
    categoria_id: Optional[int] = Field(default=None, ge=1)


class TarefaUpdate(Base):
    """Todos os campos são opcionais: o PATCH altera apenas o que for enviado."""

    titulo: Optional[str] = Field(default=None, min_length=3, max_length=120)
    descricao: Optional[str] = Field(default=None, max_length=2000)
    status: Optional[StatusTarefa] = None
    prioridade: Optional[Prioridade] = None
    prazo: Optional[date] = None
    categoria_id: Optional[int] = Field(default=None, ge=1)

    @field_validator("titulo", "status", "prioridade")
    @classmethod
    def campo_nao_nulo(cls, v):
        if v is None:
            raise ValueError("Este campo não pode ser nulo.")
        return v


class TarefaOut(Base):
    id: int
    titulo: str
    descricao: Optional[str] = None
    status: StatusTarefa
    prioridade: Prioridade
    prazo: Optional[date] = None
    categoria_id: Optional[int] = None
    criado_em: datetime
    atualizado_em: datetime
