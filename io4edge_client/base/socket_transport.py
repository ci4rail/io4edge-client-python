import socket
import struct


class SocketTransport:
    def __init__(self, host, port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        self._socket = s

    def write(self, data: bytes) -> int:
        """
        Send the data as an io4edge message to the server
        """
        hdr = struct.pack("<HL", 0xEDFE, len(data))
        return self._socket.sendall(hdr + data)

    def read(self) -> bytes:
        """
        Wait for next io4edge message from server. 
        Return payload.
        """
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
