class DomainValidationError(Exception):
    """Raised when a domain validation error occurs"""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message
