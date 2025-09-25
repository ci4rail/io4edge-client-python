# SPDX-License-Identifier: Apache-2.0
import socket
import struct
import select


class SocketTransport:
    def __init__(self, host, port, connect=True):
        self._host = host
        self._port = port
        self._socket = None
        if connect:
            self.open()

    def __enter__(self):
        if self._socket is None:
            self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._socket is not None:
            self.close()
            self._socket = None

    def open(self):
        if self._socket is None:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            self._socket.connect((self._host, self._port))
            return self
        return

    @property
    def connected(self):
        return self._socket is not None

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

    def close(self):
        self._socket.close()
