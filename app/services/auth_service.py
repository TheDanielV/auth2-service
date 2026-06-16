from __future__ import annotations

from sqlalchemy import or_, select
from sqlalchemy.orm import Session, selectinload

from app.core.security import create_access_token, verify_secret
from app.core.logging import get_logger
from app.models import OAuthClient, User
from app.schemas.oauth import TokenResponse
from app.schemas.user import UserRead

logger = get_logger(__name__)


class AuthenticationError(ValueError):
    """Se lanza cuando las credenciales no son válidas."""


class UnsupportedGrantTypeError(ValueError):
    """Se lanza cuando el grant_type no está soportado."""


def _authenticate_client(db: Session, client_id: str, client_secret: str) -> OAuthClient:
    logger.debug(f"🔑 Autenticando cliente OAuth: {client_id}")
    client = db.scalar(select(OAuthClient).where(OAuthClient.client_id == client_id))
    if client is None or not verify_secret(client_secret, client.client_secret):
        logger.warning(f"⚠️  Fallo en autenticación de cliente: {client_id}")
        raise AuthenticationError("client_id o client_secret inválidos")
    logger.info(f"✅ Cliente OAuth autenticado correctamente: {client_id}")
    return client


def issue_token_for_password_grant(
    db: Session,
    *,
    client_id: str,
    client_secret: str,
    username: str,
    password: str,
) -> TokenResponse:
    logger.info(f"🔐 Intento de autenticación con password grant para usuario: {username}")
    client = _authenticate_client(db, client_id, client_secret)

    user = db.scalar(
        select(User)
        .options(selectinload(User.roles))
        .where(
            User.tenant_id == client.tenant_id,
            or_(User.email == username, User.username == username),
        )
    )
    if user is None or not verify_secret(password, user.password_hash):
        logger.warning(f"⚠️  Fallo en autenticación de usuario: {username}")
        raise AuthenticationError("username o password inválidos")

    logger.info(f"✅ Usuario autenticado exitosamente: {username} (ID: {user.id})")
    user_claims = UserRead.from_entity(user).model_dump(mode="json")

    token, expires_in = create_access_token(
        subject=f"user:{user.id}",
        audience=client.client_id,
        tenant_id=user_claims.get("tenant_id", user.tenant_id),
        roles=user_claims.get("roles", []),
        custom_attributes=user_claims.get("custom_attributes", {}),
        additional_claims={
            "grant_type": "password",
            "user": user_claims,
        },
    )
    logger.debug(f"📡 Token de acceso generado para usuario: {username}")
    return TokenResponse(access_token=token, expires_in=expires_in)


def issue_token_for_client_credentials(
    db: Session,
    *,
    client_id: str,
    client_secret: str,
) -> TokenResponse:
    logger.info(f"🔐 Intento de autenticación con client credentials para cliente: {client_id}")
    client = _authenticate_client(db, client_id, client_secret)

    token, expires_in = create_access_token(
        subject=f"client:{client.id}",
        audience=client.client_id,
        tenant_id=client.tenant_id,
        roles=[],
        custom_attributes={},
        additional_claims={"grant_type": "client_credentials"},
    )
    logger.debug(f"📡 Token de acceso generado para cliente: {client_id}")
    return TokenResponse(access_token=token, expires_in=expires_in)

