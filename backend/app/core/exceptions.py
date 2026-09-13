class AppException(Exception):
    status_code = 400
    code = "BAD_REQUEST"

    def __init__(self, message: str, details: list | None = None):
        super().__init__(message)
        self.message = message
        self.details = details or []


class NotFoundException(AppException):
    status_code = 404
    code = "NOT_FOUND"


class UnauthorizedException(AppException):
    status_code = 401
    code = "UNAUTHORIZED"


class ForbiddenException(AppException):
    status_code = 403
    code = "FORBIDDEN"


class BusinessRuleException(AppException):
    status_code = 422
    code = "BUSINESS_RULE_VIOLATION"


class ImportValidationException(AppException):
    status_code = 400
    code = "IMPORT_VALIDATION_ERROR"
