"""Hash de senhas (PBKDF2, biblioteca padrão) e geração/validação de tokens JWT."""
import hashlib
import hmac
import os
from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt

from .config import settings

ALGORITMO_JWT = "HS256"
ITERACOES = 210_000


def hash_senha(senha: str) -> str:
    sal = os.urandom(16)
    dk = hashlib.pbkdf2_hmac("sha256", senha.encode(), sal, ITERACOES)
    return f"pbkdf2_sha256${ITERACOES}${sal.hex()}${dk.hex()}"


def verificar_senha(senha: str, armazenado: str) -> bool:
    try:
        _, iteracoes, sal, esperado = armazenado.split("$")
        dk = hashlib.pbkdf2_hmac("sha256", senha.encode(), bytes.fromhex(sal), int(iteracoes))
        return hmac.compare_digest(dk.hex(), esperado)
    except (ValueError, TypeError):
        return False


def criar_token(usuario_id: int) -> str:
    expira = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {"sub": str(usuario_id), "exp": expira}
    return jwt.encode(payload, settings.secret_key, algorithm=ALGORITMO_JWT)


def ler_token(token: str) -> Optional[int]:
    """Retorna o id do usuário se o token for válido e não estiver expirado."""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITMO_JWT])
        return int(payload["sub"])
    except (jwt.PyJWTError, KeyError, ValueError):
        return None
