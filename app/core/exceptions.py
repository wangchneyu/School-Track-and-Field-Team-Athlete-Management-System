from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
import logging
from typing import Any

logger = logging.getLogger(__name__)


class BaseException(Exception):
    """基础异常类"""
    def __init__(self, message: str, error_code: str = "INTERNAL_ERROR", details: Any = None):
        self.message = message
        self.error_code = error_code
        self.details = details
        super().__init__(message)


class NotFoundException(BaseException):
    """资源未找到异常"""
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, "NOT_FOUND")


class ValidationException(BaseException):
    """验证异常"""
    def __init__(self, message: str, details: Any = None):
        super().__init__(message, "VALIDATION_ERROR", details)


class DatabaseException(BaseException):
    """数据库异常"""
    def __init__(self, message: str = "Database operation failed"):
        super().__init__(message, "DATABASE_ERROR")


class AuthenticationException(BaseException):
    """认证异常"""
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, "AUTHENTICATION_ERROR")


class AuthorizationException(BaseException):
    """授权异常"""
    def __init__(self, message: str = "Authorization failed"):
        super().__init__(message, "AUTHORIZATION_ERROR")


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """全局异常处理器"""
    if isinstance(exc, BaseException):
        logger.error(f"Business error: {exc.message}", exc_info=True)
        return JSONResponse(
            status_code=400,
            content={
                "error": {
                    "code": exc.error_code,
                    "message": exc.message,
                    "details": exc.details
                }
            }
        )
    
    elif isinstance(exc, RequestValidationError):
        logger.warning(f"Validation error: {exc.detail}")
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Invalid request data",
                    "details": exc.detail
                }
            }
        )
    
    elif isinstance(exc, HTTPException):
        logger.warning(f"HTTP error: {exc.status_code} - {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": "HTTP_ERROR",
                    "message": exc.detail
                }
            }
        )
    
    elif isinstance(exc, SQLAlchemyError):
        logger.error(f"Database error: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": "DATABASE_ERROR",
                    "message": "Database operation failed"
                }
            }
        )
    
    else:
        logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "Internal server error"
                }
            }
        )