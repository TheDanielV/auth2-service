from fastapi import FastAPI, status
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException as FastAPIHTTPException

from app.schemas.response import StandardErrorResponse, ResponseStatus


async def http_exception_handler(request: Request, exc: FastAPIHTTPException) -> JSONResponse:
    """
    Maneja excepciones HTTP y devuelve una respuesta estándar.
    """
    # Mapeo de códigos de estado a mensajes generales
    status_messages = {
        status.HTTP_404_NOT_FOUND: "Recurso no encontrado",
        status.HTTP_409_CONFLICT: "El recurso ya existe",
        status.HTTP_422_UNPROCESSABLE_ENTITY: "Validación fallida",
        status.HTTP_400_BAD_REQUEST: "Solicitud inválida",
        status.HTTP_401_UNAUTHORIZED: "No autorizado",
        status.HTTP_403_FORBIDDEN: "Acceso denegado",
        status.HTTP_500_INTERNAL_SERVER_ERROR: "Error interno del servidor",
    }

    # Determinar el estado
    is_success = exc.status_code < 400
    response_status = ResponseStatus.SUCCESS if is_success else ResponseStatus.FAILED

    response = StandardErrorResponse(
        status=response_status,
        detail=exc.detail or status_messages.get(exc.status_code, "Error"),
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=response.model_dump(exclude_none=True),
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Registra los exception handlers en la aplicación."""
    app.add_exception_handler(FastAPIHTTPException, http_exception_handler)

