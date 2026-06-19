"""Global error handlers and custom exceptions."""
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError


class TrustPayError(Exception):
    def __init__(self, message: str, code: str = "ERROR", status_code: int = 400):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(message)


class NotFoundError(TrustPayError):
    def __init__(self, resource: str):
        super().__init__(f"{resource} not found", "NOT_FOUND", 404)


class UnauthorizedError(TrustPayError):
    def __init__(self, detail: str = "Unauthorized"):
        super().__init__(detail, "UNAUTHORIZED", 401)


class ForbiddenError(TrustPayError):
    def __init__(self, detail: str = "Forbidden"):
        super().__init__(detail, "FORBIDDEN", 403)


class ConflictError(TrustPayError):
    def __init__(self, detail: str):
        super().__init__(detail, "CONFLICT", 409)


def register_error_handlers(app: FastAPI):

    @app.exception_handler(TrustPayError)
    async def trustpay_error_handler(request: Request, exc: TrustPayError):
        return JSONResponse(
            status_code=exc.status_code,
            content={"success": False, "error": {"code": exc.code, "message": exc.message}},
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(request: Request, exc: RequestValidationError):
        errors = [
            {"field": ".".join(str(x) for x in e["loc"]), "message": e["msg"]}
            for e in exc.errors()
        ]
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "success": False,
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Validation failed",
                    "details": errors,
                },
            },
        )

    @app.exception_handler(IntegrityError)
    async def integrity_error_handler(request: Request, exc: IntegrityError):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"success": False, "error": {"code": "CONFLICT", "message": "Resource already exists"}},
        )
