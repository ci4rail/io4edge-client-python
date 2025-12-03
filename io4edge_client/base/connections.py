from abc import ABC, abstractmethod
from functools import wraps
from typing import Tuple, Any, Optional, Protocol
import io4edge_client.api.io4edge.python.functionblock.v1alpha1.io4edge_functionblock_pb2 as FbPb  # noqa: E501


# Type variables are now defined inline with the new generic syntax


class StreamingClientProtocol(Protocol):
    """Protocol for streaming functionblock clients."""

    @property
    def connected(self) -> bool:
        """Indicates whether the client is currently connected."""
        ...

    def open(self) -> None:
        """Open the client connection."""
        ...

    def close(self) -> None:
        """Close the client connection."""
        ...

    def start_stream(self, fs_config: Any, fb_config: Any) -> None:
        """Start streaming data."""
        ...

    def stop_stream(self) -> None:
        """Stop streaming data."""
        ...

    def read_stream(self, timeout: Optional[float], stream_data: Any) -> Any:
        """Read next message from stream."""
        ...

    def function_control_set(self, fs_cmd: Any, fs_response: Any) -> None:
        """Execute function control set command."""
        ...

    def function_control_get(self, fs_cmd: Any, fs_response: Any) -> None:
        """Execute function control get command."""
        ...

    def upload_configuration(self, fs_cmd: Any) -> None:
        """Upload configuration."""
        ...

    def download_configuration(self, fs_cmd: Any, fs_response: Any) -> None:
        """Download configuration."""
        ...

    def describe(self, fs_cmd: Any, fs_response: Any) -> None:
        """Describe function block configuration."""
        ...

    def write_msg(self, msg: Any) -> None:
        """Write message to function block."""
        ...

    def read_msg(self, msg: Any, timeout: float) -> None:
        """Read message from function block."""
        ...


def connectable(func):
    """Decorator to ensure connection is established before method execution.

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


def must_be_connected(func):
    """Decorator to check if connection is established before method execution.

    Raises
    ------
    ConnectionError
        If the client is not connected.
    """

    @wraps(func)
    def check_connection(self, *args, **kwargs):
        if self.connected:
            return func(self, *args, **kwargs)
        else:
            raise ConnectionError("Client is not connected")
    return check_connection


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


class ClientConnection[ClientT: StreamingClientProtocol](
    ConnectionContextManager
):
    def __init__(self, client: ClientT):
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


class ClientConnectionStream[StreamControlStartT, StreamDataT](
    ClientConnection[StreamingClientProtocol]
):
    """Base class for streaming clients with device-specific protobuf types."""

    def __init__(self, client: StreamingClientProtocol):
        super().__init__(client)
        self.is_streaming = False

    def close(self):
        if self.is_streaming:
            self.stop_stream()
        super().close()

    @abstractmethod
    def _create_stream_data(self) -> StreamDataT:
        """Create device-specific StreamData message"""
        pass

    @abstractmethod
    def _create_default_stream_config(self) -> StreamControlStartT:
        """Create default device-specific StreamControlStart message"""
        pass

    def start_stream(
        self,
        config: Optional[StreamControlStartT] = None,
        fb_config: Optional[FbPb.StreamControl] = None
    ) -> None:
        """
        Start streaming of data.
        @param config: device-specific stream configuration
        @param fb_config: functionblock generic configuration of stream
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        """
        if config is None:
            config = self._create_default_stream_config()
        self._client.start_stream(config, fb_config)
        self.is_streaming = True

    def stop_stream(self) -> None:
        """
        Stop streaming of data.
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        """
        self._client.stop_stream()
        self.is_streaming = False

    def read_stream(
        self,
        timeout: Optional[float] = None
    ) -> Tuple[Any, StreamDataT]:
        """
        Read the next message from the stream.
        @param timeout: timeout in seconds
        @return: functionblock generic stream data, device-specific data
        @raises TimeoutError: if no data is available within timeout
        """
        stream_data = self._create_stream_data()
        generic_stream_data = self._client.read_stream(timeout, stream_data)
        return generic_stream_data, stream_data
