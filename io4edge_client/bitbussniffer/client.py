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
        Upload the configuration to the bitbus sniffer functionblock.

        The configuration defines:

        - ``ignore_crc``: retain frames with an invalid CRC when true.
        - ``baud_62500``: select 62500 baud when true, otherwise 375000 baud.
        - ``address_filter``: 32-byte bit mask selecting which addresses to
          receive. Set a bit to receive frames for its corresponding address.
        - ``min_frame_length``: discard frames shorter than this many bytes.
        - ``prepare_sender``: enable frame transmission when true; compatible
          sender hardware is required.
        - ``loopback_enable``: disable bus activity and internally loop back
          locally transmitted frames, including bitbus slave frames.
        - ``full_duplex``: keep the receiver enabled during transmission.

        @param config: configuration to upload
        @raises RuntimeError: if the command fails or the configuration is
            rejected
        @raises TimeoutError: if the command times out
        """
        self._logger.debug("Uploading configuration to bitbusSniffer")
        self._client.upload_configuration(config)

    @connectable
    def send_frame(self, bitbus_frame: bytes) -> None:
        """
        Send a frame to the bitbus.

        Sender-capable hardware is required and transmission must be enabled
        with ``ConfigurationSet.prepare_sender``. Byte 0 of ``bitbus_frame``
        is the address, byte 1 is the control field, and bytes 2 onward are the
        INFORMATION field, matching ``Sample.bitbus_frame``.

        @param bitbus_frame: complete bitbus frame to transmit
        @raises RuntimeError: if the command fails or sending is unavailable
        @raises TimeoutError: if the command times out
        """
        self._logger.debug("Sending frame to bitbusSniffer")
        fs_cmd = Pb.FunctionControlSet(bitbus_frame=bitbus_frame)
        self._client.function_control_set(
            fs_cmd, Pb.FunctionControlSetResponse())
