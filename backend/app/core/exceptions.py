class AppException(Exception):
    def __init__(self, message: str, code: str = "BAD_REQUEST", status_code: int = 400, details: dict = None):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)

class NotFoundException(AppException):
    def __init__(self, message: str = "Requested resource not found", details: dict = None):
        super().__init__(message=message, code="NOT_FOUND", status_code=404, details=details)

class AuthException(AppException):
    def __init__(self, message: str = "Authentication failed", details: dict = None):
        super().__init__(message=message, code="UNAUTHORIZED", status_code=401, details=details)

class ForbiddenException(AppException):
    def __init__(self, message: str = "Access forbidden", details: dict = None):
        super().__init__(message=message, code="FORBIDDEN", status_code=403, details=details)

class ValidationException(AppException):
    def __init__(self, message: str = "Validation failed", details: dict = None):
        super().__init__(message=message, code="VALIDATION_ERROR", status_code=422, details=details)

class AIInferenceException(AppException):
    def __init__(self, message: str = "AI inference failed", details: dict = None):
        super().__init__(message=message, code="AI_INFERENCE_ERROR", status_code=500, details=details)
