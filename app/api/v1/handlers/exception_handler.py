from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.api.v1.handlers.exceptions import AppException
from app.api.v1.schemas.error import ErrorResponse


def register_exception_handlers(app: FastAPI):
    @app.exception_handler(AppException)
    async def handle_app_exceptions(_, exc: AppException):
        response = ErrorResponse(
            error=exc.error_code,
            detail=exc.message,
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=response.model_dump(),
        )
