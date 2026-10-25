"""Dependências reutilizáveis das rotas (autenticação)."""
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from .database import get_db
from .models import Usuario
from .security import ler_token

# auto_error=False para devolvermos sempre 401 com mensagem própria
esquema_bearer = HTTPBearer(auto_error=False, description="Cole o token JWT obtido em /auth/login")


def usuario_atual(
    credenciais: Optional[HTTPAuthorizationCredentials] = Depends(esquema_bearer),
    db: Session = Depends(get_db),
) -> Usuario:
    nao_autorizado = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token ausente, inválido ou expirado.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if credenciais is None:
        raise nao_autorizado
    usuario_id = ler_token(credenciais.credentials)
    if usuario_id is None:
        raise nao_autorizado
    usuario = db.get(Usuario, usuario_id)
    if usuario is None:
        raise nao_autorizado
    return usuario
