import logging
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from app.core.exceptions import AppException, UnauthorizedException

logger = logging.getLogger(__name__)


def _error(
    status: int, code: str, message: str, details: list | None = None, headers=None
):
    body = {"error": {"code": code, "message": message, "details": details or []}}
    return JSONResponse(status_code=status, content=body, headers=headers)


def register_exception_handlers(app: FastAPI) -> None:

    @app.exception_handler(AppException)
    async def handle_app_exception(request: Request, exc: AppException):
        headers = (
            {"WWW-Authenticate": "Bearer"}
            if isinstance(exc, UnauthorizedException)
            else None
        )
        return _error(
            exc.status_code, exc.code, exc.message, details=exc.details, headers=headers
        )

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(request: Request, exc: RequestValidationError):
        details = [
            {"field": ".".join((str(p) for p in err["loc"][1:])), "message": err["msg"]}
            for err in exc.errors()
        ]
        return _error(400, "VALIDATION_ERROR", "Invalid request", details)

    @app.exception_handler(IntegrityError)
    async def handle_integrity_error(request: Request, exc: IntegrityError):
        logger.warning("Integrity error", exc_info=exc)
        return _error(
            409, "CONFLICT", "That record already exists. Refresh and try again."
        )

    @app.exception_handler(Exception)
    async def handle_unexpected(request: Request, exc: Exception):
        logger.exception("Unexpected error")
        return _error(500, "INTERNAL_ERROR", "Something went wrong")
