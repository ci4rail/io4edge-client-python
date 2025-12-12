# SPDX-License-Identifier: Apache-2.0
from io4edge_client.base.connections import ClientConnectionStream, connectable
from io4edge_client.base.logging import io4edge_client_logger
from io4edge_client.functionblock import Client as FbClient
import io4edge_client.api.analogInTypeA.python.analogInTypeA.v1alpha1.analogInTypeA_pb2 as Pb  # noqa: E501


class Client(
    ClientConnectionStream[FbClient, Pb.StreamControlStart, Pb.StreamData]
):
    """
    analogInTypeA functionblock client.
    @param addr: address of io4edge function block (mdns name or "ip:port" address)
    @param command_timeout: timeout for commands in seconds
    """

    def __init__(
        self,
        addr: str,
        command_timeout: int = 5,
        connect: bool = True
    ) -> None:
        self._logger = io4edge_client_logger("analogintypea.Client")
        self._logger.debug(
            "Initializing analogInTypeA client for addr='%s', timeout=%s",
            addr, command_timeout
        )
        fb_client = FbClient(
            "_io4edge_analogInTypeA._tcp", addr, command_timeout,
            connect=connect
        )
        super().__init__(fb_client)

    def _create_stream_data(self) -> Pb.StreamData:
        """Create analogInTypeA-specific StreamData message"""
        return Pb.StreamData()

    def _create_default_stream_config(self) -> Pb.StreamControlStart:
        """Create default analogInTypeA-specific StreamControlStart message"""
        return Pb.StreamControlStart()

    @connectable
    def upload_configuration(  # type: ignore[override]
        self, config: Pb.ConfigurationSet
    ) -> None:
        """
        Upload the configuration to the analogInTypeA functionblock.
        @param config: configuration to upload
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        """
        self._logger.debug("Uploading configuration to analogInTypeA")
        self._client.upload_configuration(config)
        self._logger.info(
            "Configuration uploaded successfully to analogInTypeA"
        )

    @connectable
    def download_configuration(  # type: ignore[override]
        self
    ) -> Pb.ConfigurationGetResponse:
        """
        Download the configuration from the analogInTypeA functionblock.
        @return: actual configuration
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        """
        self._logger.debug("Downloading configuration from analogInTypeA")
        fs_response = Pb.ConfigurationGetResponse()
        self._client.download_configuration(Pb.ConfigurationGet(), fs_response)
        self._logger.info("Configuration downloaded successfully from "
                          "analogInTypeA")
        return fs_response

    @connectable
    def value(self) -> float:
        """
        Read the current analog input level.

        @return: current analog input level, range -1..+1 for min/max
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        """
        self._logger.debug("Reading current analog input value")
        fs_cmd = Pb.FunctionControlGet()
        fs_response = Pb.FunctionControlGetResponse()
        self._client.function_control_get(fs_cmd, fs_response)
        value = fs_response.value
        self._logger.debug("Read analog value: %s", value)
        return value
