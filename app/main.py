"""Ponto de entrada da API de Tarefas e Categorias."""
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from . import models  # noqa: F401  (garante o registro dos modelos antes do create_all)
from .config import settings
from .database import Base, engine
from .routers import auth, categorias, tarefas


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Cria as tabelas caso ainda não existam (equivalente ao arquivo schema.sql)
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="API de Tarefas e Categorias",
    description=(
        "API REST para gerenciamento de tarefas organizadas por categorias, "
        "com autenticação JWT. Trabalho final de Arquitetura e Desenvolvimento de APIs."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# CORS: apenas as origens listadas em CORS_ORIGINS, métodos e cabeçalhos estritamente necessários.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
    allow_credentials=False,
)


@app.exception_handler(RequestValidationError)
async def tratar_validacao(request: Request, exc: RequestValidationError):
    """Converte erros de validação do Pydantic em 400 com mensagens legíveis."""
    erros = [
        {
            "campo": ".".join(str(p) for p in e["loc"] if p not in ("body", "query", "path")),
            "mensagem": e["msg"],
        }
        for e in exc.errors()
    ]
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": "Dados inválidos.", "erros": erros},
    )


app.include_router(auth.router)
app.include_router(categorias.router)
app.include_router(tarefas.router)


@app.get("/", tags=["Sistema"])
def raiz():
    return {"mensagem": "API de Tarefas e Categorias no ar.", "documentacao": "/docs"}
