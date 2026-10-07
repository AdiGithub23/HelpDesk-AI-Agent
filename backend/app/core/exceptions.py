class AppError(Exception):
    """Base class for all errors raised by services."""


class NotFoundError(AppError):
    pass


class PermissionDeniedError(AppError):
    pass


class InvalidTransitionError(AppError):
    pass
