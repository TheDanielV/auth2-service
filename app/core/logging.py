import logging
import logging.config
from pathlib import Path
from datetime import datetime

def setup_logging(log_level: str = "INFO", log_dir: str = "logs") -> None:
    """
    Configura el sistema de logging para la aplicación FastAPI.

    Args:
        log_level: Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: Directorio donde se guardarán los archivos de log
    """

    # Crear directorio de logs si no existe
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)

    # Nombre del archivo de log con timestamp
    log_file = log_path / f"authservice_{datetime.now().strftime('%Y%m%d')}.log"

    # Configuración de logging
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "detailed": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            },
            "simple": {
                "format": "%(levelname)s - %(message)s"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": log_level,
                "formatter": "simple",
                "stream": "ext://sys.stdout"
            },
            "file": {
                "class": "logging.FileHandler",
                "level": log_level,
                "formatter": "detailed",
                "filename": str(log_file),
                "encoding": "utf-8"
            }
        },
        "loggers": {
            "app": {
                "level": log_level,
                "handlers": ["console", "file"],
                "propagate": False
            },
            "sqlalchemy.engine": {
                "level": "WARNING",
                "handlers": ["file"],
                "propagate": False
            },
            "uvicorn": {
                "level": log_level,
                "handlers": ["console", "file"],
                "propagate": False
            }
        },
        "root": {
            "level": log_level,
            "handlers": ["console", "file"]
        }
    }

    logging.config.dictConfig(logging_config)


def get_logger(name: str) -> logging.Logger:
    """
    Obtiene un logger configurado para un módulo específico.

    Args:
        name: Nombre del módulo (usualmente __name__)

    Returns:
        Logger configurado
    """
    return logging.getLogger(name)

