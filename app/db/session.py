from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings
from app.core.logging import get_logger
from app.db.base import Base
import app.models  # noqa: F401

logger = get_logger(__name__)


def _get_connect_args() -> dict[str, bool]:
    if settings.database_url.startswith("sqlite"):
        return {"check_same_thread": False}
    return {}


engine = create_engine(
    settings.database_url,
    future=True,
    pool_pre_ping=True,
    connect_args=_get_connect_args(),
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
    class_=Session,
)


def init_db() -> None:
    try:
        logger.info("🔄 Iniciando conexión a la base de datos...")
        logger.debug(f"📍 URL de conexión: {settings.database_url}")

        Base.metadata.create_all(bind=engine)

        logger.info("✅ Base de datos conectada correctamente")
        logger.info(f"📊 Tablas creadas/verificadas: {', '.join(Base.metadata.tables.keys()) if Base.metadata.tables else 'ninguna'}")
        logger.info("✅ Inicialización de BD completada exitosamente")

    except Exception as e:
        logger.error(f"❌ Error al conectar o inicializar la base de datos: {str(e)}", exc_info=True)
        raise

