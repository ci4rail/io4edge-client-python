# SPDX-License-Identifier: Apache-2.0
import socket
import struct
import select

from io4edge_client.base.connections import ClientConnection
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
            self._socket.close()
            self._socket = None
            logger.info(f"Disconnected from {self._host}:{self._port}")
        else:
            logger.warning(f"Socket to {self._host}:{self._port} already disconnected")

    def write(self, data: bytes) -> int:
        """
        Send the data as an io4edge message to the server
        """
        hdr = struct.pack("<HL", 0xEDFE, len(data))
        return self._socket.sendall(hdr + data)

    def read(self, timeout) -> bytes:
        """
        Wait for next io4edge message from server.
        Return payload.
        If timeout is not None, raise TimeoutError if no message is received within timeout seconds.
        """
        if timeout is not None:
            ready = select.select([self._socket], [], [], timeout)
            if not ready[0]:
                raise TimeoutError("timeout")

        hdr = self._rcv_all(6)
        if hdr[0:2] == b"\xfe\xed":
            len = struct.unpack("<L", hdr[2:6])[0]
            data = self._rcv_all(len)
            return data
        raise RuntimeError("bad magic")

    def _rcv_all(self, data_len: int) -> bytes:
        remaining = data_len
        buf = bytearray()
        while remaining > 0:
            data = self._socket.recv(remaining)
            buf.extend(data)
            remaining -= len(data)
        return buf
