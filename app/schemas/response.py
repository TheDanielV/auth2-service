from enum import Enum
from typing import Generic, TypeVar, Optional, Any

from pydantic import BaseModel, Field

T = TypeVar("T")


class ResponseStatus(str, Enum):
    """Estados de respuesta."""
    SUCCESS = "success"
    FAILED = "failed"


class StandardResponse(BaseModel, Generic[T]):
    """Respuesta estándar para todos los endpoints."""
    status: ResponseStatus = Field(..., description="Estado de la respuesta")
    data: Optional[T] = Field(default=None, description="Datos devueltos")
    detail: Optional[str] = Field(default=None, description="Detalle del error o mensajes adicionales")


class StandardErrorResponse(BaseModel):
    """Respuesta estándar para errores."""
    status: ResponseStatus = Field(
        default=ResponseStatus.FAILED,
        description="Estado de la respuesta"
    )
    data: Optional[Any] = Field(default=None, description="Datos adicionales del error")
    detail: str = Field(..., description="Mensaje de error")

