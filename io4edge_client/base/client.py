# SPDX-License-Identifier: Apache-2.0
from zeroconf import Zeroconf

from io4edge_client.base.connections import ClientConnection, connectable
from .socket_transport import SocketTransport
import io4edge_client.api.io4edge.python.functionblock.v1alpha1.io4edge_functionblock_pb2 as FbPb


class Client(ClientConnection):
    def __init__(self, service: str, addr: str, connect=True):
        # detect if addr is a service name or an IP address
        try:
            ip, port = self._net_address_split(addr)
        except ValueError:
            # addr may be a service name
            ip, port = self._find_mdns(addr + "." + service)

        if ip is None:
            raise RuntimeError("service not found")

        self._transport = SocketTransport(ip, port, connect)

        super().__init__(self._transport)

    @connectable
    def write_msg(self, msg):
        """
        Marshall msg and write it to the server
        """
        data = msg.SerializeToString()
        self._transport.write(data)

    @connectable
    def read_msg(self, msg, timeout=None):
        """
        Wait for next message from server. Unmarshall it to msg.
        Pass msg as a protobuf message type with the expected type.
        If timeout is not None, raise TimeoutError if no message is received within timeout seconds.
        """
        data = self._transport.read(timeout)
        try:
            msg.ParseFromString(bytes(data))
        except Exception as e:
            # msg2 = FbPb.Response()
            # msg2.ParseFromString(bytes(data))
            raise RuntimeError("Failed to parse message") from e

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
            raise ValueError(
                "service address not parseable (one of these are missing: instance, service, protocol)"
            )
        service = fields[-2] + "." + fields[-1]
        instance = ".".join(fields[:-2])
        return instance, service

    @staticmethod
    def _find_mdns(service: str):
        """
        Find a service using mDNS
        :param service: service name with protocol (e.g. S101-IOU01-USB-EXT-1._io4edge-core._tcp)
        """
        zeroconf = Zeroconf()
        instance, service = Client._split_service(service)

        service += ".local."
        instance = instance + "." + service

        # print("Looking for service %s %s" % (service, instance))

        info = zeroconf.get_service_info(type_=service, name=instance)
        if info:
            rv = info.parsed_addresses()[0], info.port
        else:
            rv = None, 0
        zeroconf.close()
        return rv
