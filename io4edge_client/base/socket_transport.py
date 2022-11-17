import socket
import struct

class SocketTransport:
    def __init__(self, host, port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        self._socket = s

    def write_msg(self, data: bytes ) -> int:
        hdr = struct.pack('<HL', 0xEDFE, len(data))
        return self._socket.sendall(hdr+data)

    def read_msg(self) -> bytes:
        hdr = self.rcv_all(6)
        if hdr[0:2] == b'\xfe\xed':
            len = struct.unpack('<L', hdr[2:6])[0]
            data = self.rcv_all(len)
            return data
        raise RuntimeError('bad magic')

    def _rcv_all(self, n: int) -> bytes:
        remaining = n
        buf = bytearray()
        while remaining > 0:
            data = self._socket.recv(remaining)
            buf.extend(data)
            remaining -= len(data)
        return buf
