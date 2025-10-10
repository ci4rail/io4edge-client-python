# SPDX-License-Identifier: Apache-2.0
from io4edge_client.base.connections import ClientConnectionStream, connectable
from io4edge_client.functionblock import Client as FbClient
import io4edge_client.api.bitbusSniffer.python.bitbusSniffer.v1.bitbusSniffer_pb2 as Pb


class Client(ClientConnectionStream[Pb.StreamControlStart, Pb.StreamData]):
    """
    bitbus sniffer functionblock client.
    @param addr: address of io4edge function block (mdns name or "ip:port" address)
    @param command_timeout: timeout for commands in seconds
    """

    def __init__(self, addr: str, command_timeout=5):
        super().__init__(FbClient("_io4edge_bitbusSniffer._tcp", addr, command_timeout))

    def _create_stream_data(self) -> Pb.StreamData:
        """Create bitbusSniffer-specific StreamData message"""
        return Pb.StreamData()

    def _create_default_stream_config(self) -> Pb.StreamControlStart:
        """Create default bitbusSniffer-specific StreamControlStart message"""
        return Pb.StreamControlStart()

    @connectable
    def upload_configuration(self, config: Pb.ConfigurationSet):
        """
        Upload the configuration to the bitbus functionblock.
        @param config: configuration to upload
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        """
        self._client.upload_configuration(config)
