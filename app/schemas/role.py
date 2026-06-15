from pydantic import BaseModel, ConfigDict, Field


class RoleCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    permissions: list[str] = Field(default_factory=list)


class RoleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tenant_id: int
    name: str
    permissions: list[str] = Field(default_factory=list)

