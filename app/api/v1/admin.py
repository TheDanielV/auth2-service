from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies.db import get_db
from app.schemas.client import OAuthClientCreate, OAuthClientPoliciesUpdate, OAuthClientRead
from app.schemas.response import StandardResponse, ResponseStatus, StandardErrorResponse
from app.schemas.role import RoleCreate, RoleRead
from app.schemas.tenant import TenantCreate, TenantRead
from app.schemas.user import UserCreate, UserRead
from app.services.admin_service import (
    EntityAlreadyExistsError,
    EntityNotFoundError,
    PolicyValidationError,
    create_oauth_client,
    create_role,
    create_tenant,
    create_user,
    update_oauth_client_password_policies,
)

router = APIRouter()


@router.post("/tenants", response_model=TenantRead, status_code=status.HTTP_201_CREATED)
def create_tenant_endpoint(payload: TenantCreate, db: Session = Depends(get_db)) -> TenantRead:
    try:
        tenant = create_tenant(db, payload)
    except EntityAlreadyExistsError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return TenantRead.model_validate(tenant)


@router.post("/{tenant_id}/clients", response_model=OAuthClientRead, status_code=status.HTTP_201_CREATED)
def create_client_endpoint(
    tenant_id: int,
    payload: OAuthClientCreate,
    db: Session = Depends(get_db),
) -> OAuthClientRead:
    try:
        client = create_oauth_client(db, tenant_id, payload)
    except EntityNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except PolicyValidationError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    except EntityAlreadyExistsError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return OAuthClientRead.model_validate(client)


@router.put("/{tenant_id}/clients/{client_id}/password-policies", response_model=OAuthClientRead)
def update_client_password_policies_endpoint(
    tenant_id: int,
    client_id: str,
    payload: OAuthClientPoliciesUpdate,
    db: Session = Depends(get_db),
) -> OAuthClientRead:
    try:
        policies_list = []
        for policy in payload.password_policies:
            if isinstance(policy, str):
                policies_list.append(policy)
            else:
                policy_dict = policy.model_dump(mode="json")
                # Si el nombre es un enum, usar su valor
                if isinstance(policy_dict.get("name"), dict) and "name" in policy_dict:
                    policy_dict["name"] = policy.name.value if hasattr(policy.name, "value") else str(policy.name)
                policies_list.append(policy_dict)

        client = update_oauth_client_password_policies(
            db,
            tenant_id,
            client_id,
            policies_list,
        )
    except EntityNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return OAuthClientRead.model_validate(client)


@router.post("/{tenant_id}/users", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user_endpoint(
    tenant_id: int,
    payload: UserCreate,
    db: Session = Depends(get_db),
) -> UserRead:
    try:
        user = create_user(db, tenant_id, payload)
    except EntityNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except PolicyValidationError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    except EntityAlreadyExistsError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc

    return UserRead.from_entity(user)


@router.post("/{tenant_id}/roles", response_model=RoleRead, status_code=status.HTTP_201_CREATED)
def create_role_endpoint(
    tenant_id: int,
    payload: RoleCreate,
    db: Session = Depends(get_db),
) -> RoleRead:
    try:
        role = create_role(db, tenant_id, payload)
    except EntityNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except EntityAlreadyExistsError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc

    return RoleRead(
        id=role.id,
        tenant_id=role.tenant_id,
        name=role.name,
        permissions=[permission.name for permission in role.permissions],
    )

