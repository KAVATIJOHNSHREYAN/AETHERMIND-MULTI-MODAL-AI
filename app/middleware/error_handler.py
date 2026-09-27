from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.core.exceptions import BaseAppException
from app.logging.logger import logger
import traceback

async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catches unexpected exceptions and formats uniform API error responses"""
    logger.error(f"Unhandled Exception on [{request.method} {request.url.path}]: {str(exc)}")
    logger.error(traceback.format_exc())

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "message": "An unexpected internal server error occurred.",
            "error_code": "INTERNAL_SERVER_ERROR",
            "data": None
        }
    )

async def app_exception_handler(request: Request, exc: BaseAppException) -> JSONResponse:
    """Handles custom domain application exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.message,
            "error_code": exc.code,
            "data": None
        }
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handles Pydantic request body validation failures"""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "message": "Input validation error",
            "error_code": "VALIDATION_ERROR",
            "data": {"errors": exc.errors()}
        }
    )
