from fastapi import FastAPI
from app.core.config import settings
from app.api.v1 import health

app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
)

app.include_router(health.router, prefix="/api/v1", tags=["health"])

@app.get("/")
def root():
    return {"message": f"Bienvenido a {settings.app_name}"}