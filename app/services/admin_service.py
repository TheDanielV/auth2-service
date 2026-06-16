from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.core.security import hash_secret
from app.models import OAuthClient, Permission, Role, Tenant, User
from app.schemas.client import OAuthClientCreate
from app.schemas.role import RoleCreate
from app.schemas.tenant import TenantCreate
from app.schemas.user import UserCreate
from app.services.password_policy import PasswordPolicyValidationError, validate_password_with_policies


class EntityAlreadyExistsError(ValueError):
    """Se lanza cuando una entidad viola una restricción única."""


class EntityNotFoundError(LookupError):
    """Se lanza cuando la entidad solicitada no existe."""


class PolicyValidationError(ValueError):
    """Se lanza cuando una contraseña no cumple la política configurada."""


def _get_tenant_or_raise(db: Session, tenant_id: int) -> Tenant:
    tenant = db.get(Tenant, tenant_id)
    if tenant is None:
        raise EntityNotFoundError("Tenant no encontrado")
    return tenant


def create_tenant(db: Session, payload: TenantCreate) -> Tenant:
    tenant = Tenant(name=payload.name, domain=payload.domain)
    db.add(tenant)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise EntityAlreadyExistsError("Ya existe un tenant con ese dominio") from exc
    db.refresh(tenant)
    return tenant


def create_oauth_client(db: Session, tenant_id: int, payload: OAuthClientCreate) -> OAuthClient:
    _get_tenant_or_raise(db, tenant_id)

    password_policies = None
    if payload.password_policies:
        password_policies = []
        for policy in payload.password_policies:
            if isinstance(policy, str):
                password_policies.append(policy)
            else:
                # Convertir Pydantic BaseModel a diccionario
                policy_dict = policy.model_dump(mode="json")
                # Si el nombre es un enum, usar su valor
                if isinstance(policy_dict.get("name"), dict) and "name" in policy_dict:
                    # Manejar caso donde name podría ser serializado especialmente
                    policy_dict["name"] = policy.name.value if hasattr(policy.name, "value") else str(policy.name)
                password_policies.append(policy_dict)

    client = OAuthClient(
        tenant_id=tenant_id,
        client_id=payload.client_id,
        client_secret=hash_secret(payload.client_secret),
        redirect_uris=payload.redirect_uris,
        password_policies=password_policies,
    )
    db.add(client)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise EntityAlreadyExistsError("Ya existe un cliente con ese client_id") from exc
    db.refresh(client)
    return client


def update_oauth_client_password_policies(
    db: Session,
    tenant_id: int,
    client_id: str,
    policies: list[str | dict[str, object]],
) -> OAuthClient:
    _get_tenant_or_raise(db, tenant_id)

    client = db.scalar(
        select(OAuthClient).where(
            OAuthClient.tenant_id == tenant_id,
            OAuthClient.client_id == client_id,
        )
    )
    if client is None:
        raise EntityNotFoundError("Cliente OAuth no encontrado en este tenant")

    client.password_policies = policies
    db.add(client)
    db.commit()
    db.refresh(client)
    return client


def create_role(db: Session, tenant_id: int, payload: RoleCreate) -> Role:
    _get_tenant_or_raise(db, tenant_id)

    normalized_permissions = sorted({permission.strip() for permission in payload.permissions if permission.strip()})
    existing_permissions = {
        permission.name: permission
        for permission in db.scalars(
            select(Permission).where(Permission.name.in_(normalized_permissions))
        ).all()
    }

    permissions = []
    for permission_name in normalized_permissions:
        permission = existing_permissions.get(permission_name)
        if permission is None:
            permission = Permission(name=permission_name)
            db.add(permission)
        permissions.append(permission)

    role = Role(tenant_id=tenant_id, name=payload.name)
    role.permissions = permissions
    db.add(role)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise EntityAlreadyExistsError("Ya existe un rol con ese nombre en el tenant") from exc

    db.refresh(role)
    role = db.scalar(
        select(Role)
        .options(selectinload(Role.permissions))
        .where(Role.id == role.id)
    )
    if role is None:
        raise EntityNotFoundError("No fue posible recargar el rol creado")
    return role


def create_user(db: Session, tenant_id: int, payload: UserCreate) -> User:
    _get_tenant_or_raise(db, tenant_id)

    roles = []
    if payload.role_ids:
        roles = db.scalars(
            select(Role).where(Role.tenant_id == tenant_id, Role.id.in_(payload.role_ids))
        ).all()
        if len(roles) != len(set(payload.role_ids)):
            raise EntityNotFoundError("Uno o más roles no existen en este tenant")

    if payload.client_id:
        oauth_client = db.scalar(
            select(OAuthClient).where(
                OAuthClient.tenant_id == tenant_id,
                OAuthClient.client_id == payload.client_id,
            )
        )
        if oauth_client is None:
            raise EntityNotFoundError("El client_id no existe en este tenant")

        try:
            validate_password_with_policies(payload.password, oauth_client.password_policies)
        except PasswordPolicyValidationError as exc:
            raise PolicyValidationError(str(exc)) from exc

    user = User(
        tenant_id=tenant_id,
        email=payload.email,
        username=payload.username,
        password_hash=hash_secret(payload.password),
        custom_attributes=payload.custom_attributes,
    )
    user.roles = roles
    db.add(user)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise EntityAlreadyExistsError("El email o username ya existe en este tenant") from exc

    db.refresh(user)
    user = db.scalar(
        select(User)
        .options(selectinload(User.roles))
        .where(User.id == user.id)
    )
    if user is None:
        raise EntityNotFoundError("No fue posible recargar el usuario creado")
    return user

