"""Custom exceptions for transportation service integrations."""


class ServiceError(Exception):
    """Base exception for service errors."""

    def __init__(self, service_id: str, message: str):
        self.service_id = service_id
        self.message = message
        super().__init__(f"[{service_id}] {message}")


class ServiceUnavailableError(ServiceError):
    """Raised when a service API is unreachable."""
    pass


class AuthenticationError(ServiceError):
    """Raised when service credentials are invalid."""
    pass


class RateLimitError(ServiceError):
    """Raised when API rate limits are exceeded."""
    pass
