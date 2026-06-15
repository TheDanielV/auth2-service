from typing import Annotated

from fastapi import APIRouter, Depends, Form, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_jwks
from app.dependencies.db import get_db
from app.schemas.oauth import JWKSResponse, TokenResponse
from app.services.auth_service import (
    AuthenticationError,
    issue_token_for_client_credentials,
    issue_token_for_password_grant,
)

router = APIRouter()


@router.post("/oauth/token", response_model=TokenResponse)
def issue_token(
    grant_type: Annotated[str, Form(...)],
    client_id: Annotated[str | None, Form()] = None,
    client_secret: Annotated[str | None, Form()] = None,
    username: Annotated[str | None, Form()] = None,
    password: Annotated[str | None, Form()] = None,
    db: Session = Depends(get_db),
) -> TokenResponse:
    if not client_id or not client_secret:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="client_id y client_secret son obligatorios",
        )

    try:
        if grant_type == "password":
            if not username or not password:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="username y password son obligatorios para grant_type=password",
                )
            return issue_token_for_password_grant(
                db,
                client_id=client_id,
                client_secret=client_secret,
                username=username,
                password=password,
            )

        if grant_type == "client_credentials":
            return issue_token_for_client_credentials(
                db,
                client_id=client_id,
                client_secret=client_secret,
            )
    except AuthenticationError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="grant_type no soportado. Usa password o client_credentials",
    )


@router.get("/.well-known/jwks.json", response_model=JWKSResponse)
def jwks() -> JWKSResponse:
    return JWKSResponse.model_validate(get_jwks())

