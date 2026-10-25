import os

# Precisa ser definido ANTES de importar a aplicação
os.environ["SECRET_KEY"] = "chave-apenas-para-testes"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app


@pytest.fixture()
def client():
    """Cliente de teste com um banco SQLite em memória, novo a cada teste."""
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    Sessao = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    def override_get_db():
        db = Sessao()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)  # sem "with": não executa o lifespan (que usa o banco real)
    app.dependency_overrides.clear()


def _cadastrar_e_logar(client, email="maria@exemplo.com"):
    client.post("/auth/register", json={"nome": "Maria Silva", "email": email, "senha": "senhaSegura123"})
    r = client.post("/auth/login", json={"email": email, "senha": "senhaSegura123"})
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


@pytest.fixture()
def auth(client):
    return _cadastrar_e_logar(client)


@pytest.fixture()
def auth_outro(client):
    return _cadastrar_e_logar(client, email="joao@exemplo.com")
