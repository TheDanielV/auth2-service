from pydantic import BaseModel, ConfigDict, Field


class TenantCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    domain: str = Field(..., min_length=3, max_length=255)


class TenantRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    domain: str

