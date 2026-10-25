"""Configurações lidas de variáveis de ambiente (arquivo .env opcional)."""
import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    database_url: str
    secret_key: str
    access_token_expire_minutes: int
    cors_origins: list[str]


def carregar_configuracoes() -> Settings:
    secret_key = os.getenv("SECRET_KEY")
    if not secret_key:
        raise RuntimeError(
            "Variável de ambiente SECRET_KEY não definida. "
            "Copie .env.example para .env e defina um valor."
        )
    origens = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173")
    return Settings(
        database_url=os.getenv("DATABASE_URL", "sqlite:///./tarefas.db"),
        secret_key=secret_key,
        access_token_expire_minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60")),
        cors_origins=[o.strip() for o in origens.split(",") if o.strip()],
    )


settings = carregar_configuracoes()
