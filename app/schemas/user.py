from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator


class UserCreate(BaseModel):
    email: str | None = Field(default=None, max_length=255)
    username: str | None = Field(default=None, max_length=100)
    password: str = Field(..., min_length=8, max_length=255)
    custom_attributes: dict[str, Any] = Field(default_factory=dict)
    role_ids: list[int] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_identity(self) -> "UserCreate":
        if not self.email and not self.username:
            raise ValueError("Debe enviar email o username")
        return self


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tenant_id: int
    email: str | None
    username: str | None
    custom_attributes: dict[str, Any]
    roles: list[str] = Field(default_factory=list)

    @classmethod
    def from_entity(cls, user: Any) -> "UserRead":
        data: dict[str, Any] = {}
        for field_name in cls.model_fields:
            if not hasattr(user, field_name):
                continue
            value = getattr(user, field_name)
            if field_name == "roles":
                # Admite listas de strings o entidades con atributo `name`.
                data[field_name] = [
                    item if isinstance(item, str) else getattr(item, "name", str(item))
                    for item in (value or [])
                ]
            else:
                data[field_name] = value
        return cls.model_validate(data)

