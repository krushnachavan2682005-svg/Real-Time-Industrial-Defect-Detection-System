from fastapi import Request
from fastapi.responses import JSONResponse
from src.core.exceptions import ApplicationError

from src.api.schemas import ErrorResponse, ErrorDetail


def industrial_exception_handler(request: Request, exc: ApplicationError):
    # Mapping domain exception to HTTP status codes based on common patterns
    status_code = 500

    # Just a general mapping logic, can be refined based on specific exceptions
    if "Validation" in exc.__class__.__name__ or "Config" in exc.__class__.__name__:
        status_code = 400
    elif "Integration" in exc.__class__.__name__ or "Mapping" in exc.__class__.__name__:
        status_code = 500

    return JSONResponse(
        status_code=status_code,
        content=ErrorResponse(
            error=ErrorDetail(code=exc.__class__.__name__, message=str(exc))
        ).model_dump(),
    )


def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error=ErrorDetail(
                code="INTERNAL_SERVER_ERROR", message="An unexpected error occurred."
            )
        ).model_dump(),
    )
