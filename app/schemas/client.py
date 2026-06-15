from pydantic import BaseModel, ConfigDict, Field


class OAuthClientCreate(BaseModel):
    client_id: str = Field(..., min_length=3, max_length=120)
    client_secret: str = Field(..., min_length=8, max_length=255)
    redirect_uris: list[str] = Field(default_factory=list)


class OAuthClientRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tenant_id: int
    client_id: str
    redirect_uris: list[str]

