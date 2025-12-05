class CommandTemporaryUnavailableError(Exception):
    """Exception raised when a command cannot be processed temporarily."""


class InvalidStateError(Exception):
    """Exception raised when an operation is attempted in an invalid state."""


class UnknownError(Exception):
    """Exception raised when an unknown error occurs."""
