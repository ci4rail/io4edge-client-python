# SPDX-License-Identifier: Apache-2.0
from typing import Tuple, Any
from io4edge_client.base.connections import ClientConnection, connectable
from io4edge_client.base.logging import io4edge_client_logger
from io4edge_client.functionblock import Client as FbClient
import io4edge_client.api.colorLED.python.colorLED.v1alpha1.colorLED_pb2 as Pb  # noqa: E501


class Client(ClientConnection):
    """
    colorLED functionblock client.
    @param addr: address of io4edge function block (mdns name or "ip:port" address)
    @param command_timeout: timeout for commands in seconds
    """

    def __init__(
        self,
        addr: str,
        command_timeout: int = 5,
        connect: bool = False
    ) -> None:
        self._logger = io4edge_client_logger("colorLED.Client")
        self._logger.debug("Initializing colorLED client")
        fb_client = FbClient(
            "_io4edge_colorLED._tcp", addr, command_timeout,
            connect=connect
        )
        super().__init__(fb_client)
        # Type hint for better IDE support
        self._client: FbClient = self._client

    @connectable
    def describe(self) -> Pb.ConfigurationDescribeResponse:
        """
        Get the description from the colorLED functionblock.
        @return: description from the colorLED functionblock
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        """
        fs_response = Pb.ConfigurationDescribeResponse()
        self._client.describe(Pb.ConfigurationDescribe(), fs_response)
        return fs_response

    @connectable
    def set(self, channel: int, color: Pb.Color, blink: bool) -> None:
        """
        Set the state of a single output.
        @param channel: channel number
        @param color: color to set
        @param blink: if true the LED should blink
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        """
        fs_cmd = Pb.FunctionControlSet()
        fs_cmd.channel = channel
        fs_cmd.color = color
        fs_cmd.blink = blink
        self._client.function_control_set(
            fs_cmd, Pb.FunctionControlSetResponse()
        )

    @connectable
    def get(self, channel: int) -> Tuple[Any, bool]:
        """
        Get the state of a single channel.
        @param channel: channel number
        @return: LED color and blink state
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        """
        fs_cmd = Pb.FunctionControlGet()
        fs_cmd.channel = channel
        fs_response = Pb.FunctionControlGetResponse()
        self._client.function_control_get(fs_cmd, fs_response)
        return fs_response.color, fs_response.blink
