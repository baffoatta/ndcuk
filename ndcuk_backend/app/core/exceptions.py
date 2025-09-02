from fastapi import HTTPException, status

class NDCException(HTTPException):
    """Base exception for NDC backend"""
    pass

class AuthenticationException(NDCException):
    def __init__(self, detail: str = "Could not validate credentials"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)

class AuthorizationException(NDCException):
    def __init__(self, detail: str = "Not enough permissions"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)

class NotFoundException(NDCException):
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)

class ValidationException(NDCException):
    def __init__(self, detail: str = "Validation error"):
        super().__init__(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=detail)

class ConflictException(NDCException):
    def __init__(self, detail: str = "Resource conflict"):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)