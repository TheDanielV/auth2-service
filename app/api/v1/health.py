from fastapi import APIRouter
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)

@router.get("/health")
def health_check():
    logger.info("✅ Health check realizado - Sistema operativo")
    return {"status": "ok"}