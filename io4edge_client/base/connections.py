from abc import ABC, abstractmethod
from functools import wraps
from typing import Tuple, Any
import io4edge_client.api.io4edge.python.functionblock.v1alpha1.io4edge_functionblock_pb2 as FbPb


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


# Type variables for the protobuf message types using new syntax
type StreamControlStartT = object
type StreamDataT = object

class ClientConnectionStream[StreamControlStartT, StreamDataT](ClientConnection):
    """Base class for streaming clients with device-specific protobuf types."""

    def __init__(self, client: AbstractConnection):
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

    def start_stream(self, config: StreamControlStartT = None, fb_config: FbPb.StreamControl = None):
        """
        Start streaming of data.
        @param config: device-specific stream configuration (uses default if None)
        @param fb_config: functionblock generic configuration of the stream
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        """
        if config is None:
            config = self._create_default_stream_config()
        self._client.start_stream(config, fb_config)
        self.is_streaming = True

    def stop_stream(self):
        """
        Stop streaming of data.
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        """
        self._client.stop_stream()
        self.is_streaming = False

    def read_stream(self, timeout=None) -> Tuple[Any, StreamDataT]:
        """
        Read the next message from the stream.
        @param timeout: timeout in seconds
        @return: functionblock generic stream data (deliveryTimestampUs, sequence), device-specific stream data
        @raises TimeoutError: if no data is available within the timeout
        """
        stream_data = self._create_stream_data()
        generic_stream_data = self._client.read_stream(timeout, stream_data)
        return generic_stream_data, stream_data
