from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import oauth
from app.api.exception_handlers import register_exception_handlers
from app.core.config import settings
from app.core.logging import setup_logging, get_logger
from app.db.session import init_db
from app.api.v1 import health
from app.api.v1 import admin

# Configurar logging
setup_logging(log_level="INFO")
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Startup
    logger.info("=" * 60)
    logger.info(f"🚀 Iniciando {settings.app_name}")
    logger.info(f"🔧 Modo: {'DEBUG' if settings.debug else 'PRODUCTION'}")
    logger.info(f"🗄️  Base de datos: {settings.database_url}")

    try:
        init_db()
        logger.info("✅ Base de datos inicializada correctamente")
        logger.info("✅ Aplicación iniciada exitosamente")
        logger.info("=" * 60)
    except Exception as e:
        logger.error(f"❌ Error al inicializar la base de datos: {str(e)}", exc_info=True)
        raise

    yield

    # Shutdown
    logger.info("=" * 60)
    logger.info(f"🛑 Cerrando {settings.app_name}")
    logger.info("=" * 60)

app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)

# Registrar exception handlers
register_exception_handlers(app)

app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(admin.router, prefix="/api/v1", tags=["admin"])
app.include_router(oauth.router, tags=["oauth"])

@app.get("/")
def root():
    logger.info("📡 Acceso a endpoint raíz")
    return {"message": f"Bienvenido a {settings.app_name}"}