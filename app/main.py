from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api import oauth
from app.core.config import settings
from app.db.session import init_db
from app.api.v1 import health
from app.api.v1 import admin


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield

app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    lifespan=lifespan,
)

app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(admin.router, prefix="/api/v1", tags=["admin"])
app.include_router(oauth.router, tags=["oauth"])

@app.get("/")
def root():
    return {"message": f"Bienvenido a {settings.app_name}"}