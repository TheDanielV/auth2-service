from pydantic import BaseModel, Field


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = Field(..., gt=0)


class JWKModel(BaseModel):
    kty: str
    use: str
    kid: str
    alg: str
    n: str
    e: str


class JWKSResponse(BaseModel):
    keys: list[JWKModel]

