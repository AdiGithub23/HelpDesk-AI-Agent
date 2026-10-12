class AppError(Exception):
    """Base class for all errors raised by services."""


class NotFoundError(AppError):
    pass


class AuthenticationError(AppError):
    pass


class PermissionDeniedError(AppError):
    pass


class InvalidTransitionError(AppError):
    pass


class ConflictError(AppError):
    pass


class AIProviderError(AppError):
    """The AI provider (embeddings or chat) failed."""



