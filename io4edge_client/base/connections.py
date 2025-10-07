from abc import ABC, abstractmethod
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


class AbstractConnection(ABC):

    @property
    @abstractmethod
    def connected(self) -> bool:
        """Indicates whether the client is currently connected."""
        pass

    @abstractmethod
    def open(self) -> None:
        """Open the client connection."""
        pass

    @abstractmethod
    def close(self) -> None:
        """Close the client connection."""
        pass

class ConnectionContextManager(AbstractConnection):
    def __enter__(self):
        if not self.connected:
            self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class ClientConnection(ConnectionContextManager):
    def __init__(self, client: AbstractConnection):
        self._client = client

    @property
    def connected(self) -> bool:
        return self._client is not None and self._client.connected

    def open(self) -> None:
        if not self.connected:
            self._client.open()

    def close(self) -> None:
        if self.connected:
            self._client.close()

class ClientConnectionStream(ClientConnection):
    # TODO: must be enhanced using generics to support different stream message types
    def __init__(self, client: AbstractConnection):
        super().__init__(client)
        self.is_streaming = False

    def close(self):
        if self.is_streaming:
            self.stop_stream()
        super().close()

    @abstractmethod
    def start_stream(self, config: Pb.StreamControlStart, fb_config: FbPb.StreamControl):
        """Start streaming of transitions."""
        pass

    @abstractmethod
    def stop_stream(self):
        """Stop streaming of transitions."""
        pass

    @abstractmethod
    def read_stream(self, timeout=None):
        """Read the next message from the stream."""
        pass
