from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "Auth Service"
    debug: bool = False
    database_url: str = "sqlite:///./auth_service.db"
    cors_allow_origins: list[str] = ["*"]
    cors_allow_credentials: bool = True
    cors_allow_methods: list[str] = ["*"]
    cors_allow_headers: list[str] = ["*"]
    secret_key: str = "development-secret-key"
    issuer: str = "http://localhost:8000"
    access_token_expire_minutes: int = 60
    rsa_private_key: str | None = None
    rsa_public_key: str | None = None
    rsa_key_id: str = "authservice-main"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


def get_settings() -> Settings:
    return Settings()


settings = get_settings()
