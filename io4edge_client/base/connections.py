from abc import ABC
from functools import wraps


def connectable(func):
    """Decorator to ensure the connection is established before executing the method.

    TODO:
    - Add support for async methods
    - Add logging
    - Add timeout handling
    - Check client protocol implementation
    - support usage on classes which implement context manager
    """
    @wraps(func)
    def connect(self, *args, **kwargs):
        if self.connected:
            return func(self, *args, **kwargs)
        else:
            with self._client:
                return func(self, *args, **kwargs)
    return connect


class AbstractClient(ABC):
    @property
    def connected(self) -> bool:
        """Indicates whether the client is currently connected."""
        pass

    def open(self) -> None:
        """Open the client connection."""
        pass

    def close(self) -> None:
        """Close the client connection."""
        pass
