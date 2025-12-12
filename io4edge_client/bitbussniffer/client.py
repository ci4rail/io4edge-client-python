# SPDX-License-Identifier: Apache-2.0
from io4edge_client.base.connections import ClientConnectionStream, connectable
from io4edge_client.base.logging import io4edge_client_logger
from io4edge_client.functionblock import Client as FbClient
import io4edge_client.api.bitbusSniffer.python.bitbusSniffer.v1.bitbusSniffer_pb2 as Pb  # noqa: E501


class Client(ClientConnectionStream[Pb.StreamControlStart, Pb.StreamData]):
    """
    bitbus sniffer functionblock client.
    @param addr: address of io4edge function block (mdns name or "ip:port" address)
    @param command_timeout: timeout for commands in seconds
    """

    def __init__(
        self,
        addr: str,
        command_timeout: int = 5,
        connect: bool = True
    ) -> None:
        self._logger = io4edge_client_logger("bitbussniffer.Client")
        self._logger.debug("Initializing bitbusSniffer client")
        fb_client = FbClient(
            "_io4edge_bitbusSniffer._tcp", addr, command_timeout,
            connect=connect
        )
        super().__init__(fb_client)
        # Type hint for better IDE support
        self._client: FbClient = self._client

    def _create_stream_data(self) -> Pb.StreamData:
        """Create bitbusSniffer-specific StreamData message"""
        return Pb.StreamData()

    def _create_default_stream_config(self) -> Pb.StreamControlStart:
        """Create default bitbusSniffer-specific StreamControlStart message"""
        return Pb.StreamControlStart()

    @connectable
    def upload_configuration(self, config: Pb.ConfigurationSet) -> None:
        """
        Upload the configuration to the bitbus functionblock.
        @param config: configuration to upload
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        """
        self._logger.debug("Uploading configuration to bitbusSniffer")
        self._client.upload_configuration(config)
