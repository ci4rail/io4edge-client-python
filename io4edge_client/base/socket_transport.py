# SPDX-License-Identifier: Apache-2.0
import socket
import struct
import select
import threading
from typing import Optional

from io4edge_client.base.connections import ClientConnection, must_be_connected
from io4edge_client.base.logging import io4edge_client_logger

logger = io4edge_client_logger(__name__)


class SocketTransport(ClientConnection):
    def __init__(self, host, port, connect=True):
        self._host = host
        self._port = port
        self._socket: Optional[socket.socket] = None
        # Thread-safe connection management with reference counting
        self._connection_lock = threading.RLock()  # Reentrant lock
        self._connection_ref_count = 0

        super().__init__(self)

        if connect:
            self.open()

    def open(self):
        """Open connection with reference counting for thread safety."""
        with self._connection_lock:
            self._connection_ref_count += 1
            logger.debug("Socket connection reference count increased to %d",
                        self._connection_ref_count)

            if self._socket is None:
                logger.debug("Opening socket connection to %s:%s",
                           self._host, self._port)
                self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self._socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                self._socket.connect((self._host, self._port))
                logger.info("Connected to %s:%s", self._host, self._port)
            else:
                logger.debug("Socket already connected to %s:%s, "
                           "reference count increased", self._host, self._port)

    @property
    def connected(self):
        """Check connection status with thread safety."""
        with self._connection_lock:
            if self._socket is None:
                return False
            # Check if socket is actually still valid
            try:
                # Try to get socket option - will fail if socket is closed
                self._socket.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
                return True
            except OSError:
                # Socket is closed or invalid - reset state
                self._socket = None
                self._connection_ref_count = 0
                return False

    def close(self):
        """Close connection with reference counting for thread safety."""
        with self._connection_lock:
            if self._connection_ref_count > 0:
                self._connection_ref_count -= 1
                logger.debug("Socket connection reference count decreased to %d",
                           self._connection_ref_count)

            # Only actually close when no more references and socket is open
            if self._connection_ref_count == 0 and self._socket is not None:
                try:
                    # Shutdown first to interrupt pending operations
                    self._socket.shutdown(socket.SHUT_RDWR)
                except OSError:
                    # Socket might already be closed/disconnected
                    logger.warning("Socket to %s:%s disconnected during shutdown",
                                 self._host, self._port)
                self._socket.close()
                self._socket = None
                logger.info("Disconnected from %s:%s", self._host, self._port)
            elif self._connection_ref_count > 0:
                logger.debug("Socket still in use by %d references, keeping open",
                           self._connection_ref_count)
            else:
                logger.debug("Socket to %s:%s already disconnected",
                           self._host, self._port)

    @must_be_connected
    def write(self, data: bytes):
        """
        Send the data as an io4edge message to the server
        """
        if self._socket is not None:  # Should be guaranteed by decorator, but pylance complains
            hdr = struct.pack("<HL", 0xEDFE, len(data))
            try:
                self._socket.sendall(hdr + data)
            except OSError as e:
                raise ConnectionError("Socket error during sendall") from e
        else:
            raise ConnectionError("Socket is not connected")

    @must_be_connected
    def read(self, timeout) -> bytes:
        """
        Wait for next io4edge message from server.
        Return payload.
        If timeout is not None, raise TimeoutError if no message is received
        within timeout seconds.
        """
        if timeout is not None:
            try:
                ready = select.select([self._socket], [], [self._socket],
                                      timeout)
            except OSError as e:
                # Socket was closed or became invalid
                raise ConnectionError("socket error during select") from e
            if ready[2]:  # Exception occurred
                raise ConnectionError("socket connection aborted")
            if not ready[0]:  # No data available
                logger.debug("No data available on socket read after %s seconds", timeout)
                raise TimeoutError("Timeout")

        hdr = self._rcv_all(6, timeout)
        if hdr[0:2] == b"\xfe\xed":
            data_len = struct.unpack("<L", hdr[2:6])[0]
            data = self._rcv_all(data_len, timeout)
            return data
        raise RuntimeError("bad magic")

    @must_be_connected
    def _rcv_all(self, data_len: int, timeout=None) -> bytes:
        assert self._socket is not None  # Should be guaranteed by decorator
        remaining = data_len
        buf = bytearray()

        try:
            # Set socket timeout if specified
            original_timeout = self._socket.gettimeout()
            if timeout is not None:
                self._socket.settimeout(timeout)
        except OSError as e:
            # Socket was closed or became invalid
            raise ConnectionError("Socket is no longer valid") from e

        try:
            while remaining > 0:
                try:
                    data = self._socket.recv(remaining)
                except OSError as e:
                    # Socket was closed or became invalid during recv
                    raise ConnectionError("Socket error during recv") from e

                if not data:  # Socket closed
                    raise ConnectionError("Socket closed during recv")
                buf.extend(data)
                remaining -= len(data)
        finally:
            # Restore original timeout - handle case where socket is closed
            try:
                if self._socket is not None and original_timeout is not None:
                    self._socket.settimeout(original_timeout)
            except OSError:
                # Socket was closed, ignore the error
                pass

        return buf
