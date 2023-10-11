from starlette.exceptions import HTTPException

class HTTPError(HTTPException):
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message

class InvalidUsage(HTTPError):
    def __init__(self, message: str):
        self.status_code = 400
        self.message = message

class Unauthorized(HTTPError):
    def __init__(self, message: str):
        self.status_code = 401
        self.message = message

class Forbidden(HTTPError):
    def __init__(self, message: str):
        self.status_code = 403
        self.message = message

class NotFound(HTTPError):
    def __init__(self, message: str):
        self.status_code = 404
        self.message = message

class MethodNotAllowed(HTTPError):
    def __init__(self, message: str):
        self.status_code = 405
        self.message = message

class NotAcceptable(HTTPError):
    def __init__(self, message: str):
        self.status_code = 406
        self.message = message

class RequestTimeout(HTTPError):
    def __init__(self, message: str):
        self.status_code = 408
        self.message = message

class Conflict(HTTPError):
    def __init__(self, message: str):
        self.status_code = 409
        self.message = message

class Gone(HTTPError):
    def __init__(self, message: str):
        self.status_code = 410
        self.message = message

class ValidationError(HTTPError):
    def __init__(self, message: str):
        self.status_code = 422
        self.message = message

class UUIDValidationError(HTTPError):
    def __init__(self, message: str = "Provided id is not a valid UUID."):
        self.status_code = 422
        self.message = message
