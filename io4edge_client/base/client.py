from zeroconf import Zeroconf
from .socket_transport import SocketTransport


class Client:
    def __init__(self, addr: str):
        # self._transport = SocketTransport(ip, port)
        pass

    def write_msg(self, data: bytes) -> int:
        pass

    def read_msg(self) -> bytes:
        pass

    @staticmethod
    def _net_address_split(addr: str):
        # split string "ip:port" into tuple (ip, port)
        fields = addr.split(":")
        if len(fields) != 2:
            raise ValueError("invalid address")
        return fields[0], int(fields[1])

    @staticmethod
    def _split_service(service: str):
        fields = service.split(".")
        if len(fields) < 3:
            raise ValueError("service address not parseable (one of these are missing: instance, service, protocol)")
        service = fields[-2] + "." + fields[-1]
        instance = ".".join(fields[:-2])
        return instance, service