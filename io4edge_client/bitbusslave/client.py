# SPDX-License-Identifier: Apache-2.0
from io4edge_client.base.connections import ClientConnectionStream, connectable
from io4edge_client.base.logging import io4edge_client_logger
from io4edge_client.functionblock import Client as FbClient
import io4edge_client.api.bitbusSlave.python.bitbusSlave.v1.bitbusSlave_pb2 as Pb


class Client(ClientConnectionStream[Pb.StreamControlStart, Pb.StreamData]):
    """
    bitbus slave functionblock client.
    @param addr: address of io4edge function block (mdns name or "ip:port" address)
    @param command_timeout: timeout for commands in seconds
    """

    def __init__(
        self,
        addr: str,
        command_timeout: int = 5,
        connect: bool = True
    ) -> None:
        self._logger = io4edge_client_logger("bitbusslave.Client")
        self._logger.debug("Initializing bitbusSlave client")
        fb_client = FbClient(
            "_io4edge_bitbusSlave._tcp", addr, command_timeout,
            connect=connect
        )
        super().__init__(fb_client)
        self._client: FbClient = self._client

    def _create_stream_data(self) -> Pb.StreamData:
        return Pb.StreamData()

    def _create_default_stream_config(self) -> Pb.StreamControlStart:
        return Pb.StreamControlStart()

    @connectable
    def upload_configuration(self, config: Pb.ConfigurationSet) -> None:
        """Upload the configuration to the bitbus slave functionblock."""
        self._client.upload_configuration(config)

    @connectable
    def download_configuration(self) -> Pb.ConfigurationGetResponse:
        """Download the configuration from the bitbus slave functionblock."""
        fs_response = Pb.ConfigurationGetResponse()
        self._client.download_configuration(Pb.ConfigurationGet(), fs_response)
        return fs_response

    @connectable
    def set_tx_message(self, bitbus_information: bytes) -> None:
        """Queue the bitbus information field for the next slave response."""
        fs_cmd = Pb.FunctionControlSet(
            tx_msg=Pb.PreparedTxMsg(bitbus_information=bitbus_information)
        )
        self._client.function_control_set(
            fs_cmd, Pb.FunctionControlSetResponse())

    @connectable
    def get_state(self) -> Pb.FunctionControlGetResponse:
        """Get the current slave mode and pending transmit state."""
        fs_response = Pb.FunctionControlGetResponse()
        self._client.function_control_get(Pb.FunctionControlGet(), fs_response)
        return fs_response
