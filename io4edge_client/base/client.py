from zeroconf import Zeroconf
from .socket_transport import SocketTransport

class Client:
    def __init__(self, addr: str):
        pass

    def write_msg(self, data: bytes) -> int:
        pass

    def read_msg(self) -> bytes:
        pass
