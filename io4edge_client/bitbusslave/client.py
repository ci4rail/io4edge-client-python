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
        """
        Upload the configuration to the bitbus slave functionblock.

        The configuration defines:

        - ``slave_address``: slave address in the range 1 through 249.
        - ``max_frame_length``: maximum permitted transmit frame length;
          frames exceeding it are rejected. A value of 0 permits up to 255
          bytes.
        - ``app_wd_timeout_ms``: application watchdog timeout in the range
          500 through 60000 ms, checked with approximately 50 ms resolution.
          When the watchdog expires, the slave enters NDM mode.
        - ``idle_response``: bitbus INFORMATION field sent when no application
          transmit message is pending. If empty, the slave responds with RR.
        - ``baud_62500``: select 62500 baud when true, otherwise 375000 baud.

        @param config: configuration to upload
        @raises RuntimeError: if the command fails or the configuration is
            rejected
        @raises TimeoutError: if the command times out
        """
        self._client.upload_configuration(config)

    @connectable
    def set_tx_message(self, bitbus_information: bytes) -> None:
        """
        Queue an application message for the next master request.

        ``bitbus_information`` contains only the INFORMATION field of the
        bitbus frame. The message is rejected if the slave is in disconnected
        (NDM) mode, another transmit message is already pending, its length
        exceeds the configured ``max_frame_length``, or it is empty.

        @param bitbus_information: bitbus INFORMATION field to transmit
        @raises RuntimeError: if the command fails or the message is rejected
        @raises TimeoutError: if the command times out
        """
        fs_cmd = Pb.FunctionControlSet(
            tx_msg=Pb.PreparedTxMsg(bitbus_information=bitbus_information)
        )
        self._client.function_control_set(
            fs_cmd, Pb.FunctionControlSetResponse())

    @connectable
    def get_state(self) -> Pb.FunctionControlGetResponse:
        """
        Get the current slave mode and pending transmit-message state.

        The response contains ``mode`` and ``have_pending_tx_msg``. The mode
        is ``not_configured`` when the slave is not configured and ignores all
        master requests, ``ndm`` when it is disconnected and ignores all
        master requests, or ``nrm`` when it responds to master requests.
        ``have_pending_tx_msg`` is true while an application transmit message
        is queued.

        @return: current slave mode and whether a transmit message is pending
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        """
        fs_response = Pb.FunctionControlGetResponse()
        self._client.function_control_get(Pb.FunctionControlGet(), fs_response)
        return fs_response
