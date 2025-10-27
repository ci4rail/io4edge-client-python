# SPDX-License-Identifier: Apache-2.0
import socket
import struct
import select

from io4edge_client.base.connections import ClientConnection, must_be_connected
from io4edge_client.base.logging import io4edge_client_logger

logger = io4edge_client_logger(__name__)


class SocketTransport(ClientConnection):
    def __init__(self, host, port, connect=True):
        self._host = host
        self._port = port
        self._socket = None

        super().__init__(self)

        if connect:
            self.open()

    def open(self):
        # overrided from Connection
        if not self.connected:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            self._socket.connect((self._host, self._port))
            logger.info(f"Connected to {self._host}:{self._port}")
        else:
            logger.warning(f"Socket to {self._host}:{self._port} already connected")

    @property
    def connected(self):
        # overrided from Connection
        return self._socket is not None

    def close(self):
        # overrided from Connection
        if self.connected:
            try:
                # Shutdown the socket first to interrupt any pending operations
                self._socket.shutdown(socket.SHUT_RDWR)
            except OSError:
                # Socket might already be closed/disconnected
                pass
            self._socket.close()
            self._socket = None
            logger.info(f"Disconnected from {self._host}:{self._port}")
        else:
            logger.warning(f"Socket to {self._host}:{self._port} already disconnected")

    @must_be_connected
    def write(self, data: bytes) -> int:
        """
        Send the data as an io4edge message to the server
        """
        hdr = struct.pack("<HL", 0xEDFE, len(data))
        return self._socket.sendall(hdr + data)

    @must_be_connected
    def read(self, timeout) -> bytes:
        """
        Wait for next io4edge message from server.
        Return payload.
        If timeout is not None, raise TimeoutError if no message is received within timeout seconds.
        """
        if timeout is not None:
            ready = select.select([self._socket], [], [self._socket], timeout)
            if ready[2]:  # Exception occurred
                raise ConnectionError("Socket error detected")
            if not ready[0]:  # No data available
                raise TimeoutError("timeout")

        hdr = self._rcv_all(6, timeout)
        if hdr[0:2] == b"\xfe\xed":
            len = struct.unpack("<L", hdr[2:6])[0]
            data = self._rcv_all(len, timeout)
            return data
        raise RuntimeError("bad magic")

    @must_be_connected
    def _rcv_all(self, data_len: int, timeout=None) -> bytes:
        remaining = data_len
        buf = bytearray()

        # Set socket timeout if specified
        original_timeout = self._socket.gettimeout()
        if timeout is not None:
            self._socket.settimeout(timeout)

        try:
            while remaining > 0:
                data = self._socket.recv(remaining)
                if not data:  # Socket closed
                    raise ConnectionError("Socket closed during recv")
                buf.extend(data)
                remaining -= len(data)
        finally:
            # Restore original timeout
            self._socket.settimeout(original_timeout)

        return buf
