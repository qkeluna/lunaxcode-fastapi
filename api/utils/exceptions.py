"""Custom exception classes"""

from fastapi import HTTPException, status


class NotFoundException(HTTPException):
    """Raised when a resource is not found"""

    def __init__(self, detail: str = "Resource not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class ValidationException(HTTPException):
    """Raised when validation fails"""

    def __init__(self, detail: str = "Validation error"):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=detail
        )


class UnauthorizedException(HTTPException):
    """Raised when authentication fails"""

    def __init__(self, detail: str = "Invalid or missing API key"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)