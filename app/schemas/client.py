from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class PasswordPolicyName(str, Enum):
    """Nombres de políticas de contraseña disponibles."""
    MIN_LENGTH = "min_length"
    MIN_UPPERCASE = "min_uppercase"
    MIN_SPECIAL = "min_special"


class PasswordPolicyConfig(BaseModel):
    name: PasswordPolicyName = Field(..., description="Nombre de la política de contraseña")
    enabled: bool = True
    params: dict[str, int | str | bool] = Field(default_factory=dict)


class OAuthClientCreate(BaseModel):
    client_id: str = Field(..., min_length=3, max_length=120)
    client_secret: str = Field(..., min_length=8, max_length=255)
    redirect_uris: list[str] = Field(default_factory=list)
    password_policies: list[PasswordPolicyConfig | str] | None = Field(default=None)


class OAuthClientRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tenant_id: int
    client_id: str
    redirect_uris: list[str]
    password_policies: list[PasswordPolicyConfig | str] | None = Field(default=None)


class OAuthClientPoliciesUpdate(BaseModel):
    password_policies: list[PasswordPolicyConfig | str] = Field(default_factory=list)

