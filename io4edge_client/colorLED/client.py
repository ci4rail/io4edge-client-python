# SPDX-License-Identifier: Apache-2.0
from tabnanny import check
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
    def set(self, channel: int, color: Pb.Color | Pb.RGBColor | Tuple[int, int, int], blink: bool) -> None:
        """
        Set the state of a single output.
        @param channel: channel number
        @param color: color to set as Pb.Color, Pb.RGBColor, or a tuple of (red, green, blue) values
        @param blink: if true the LED should blink
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        @raises ValueError: if the color parameter is invalid or values are out of range
        """
        fs_cmd = Pb.FunctionControlSet()
        fs_cmd.channel = channel
        if isinstance(color, Pb.Color):
            fs_cmd.color = color
        elif isinstance(color, Pb.RGBColor):
            self._check_rgb_range(color)
            fs_cmd.rgb.CopyFrom(color)
        elif isinstance(color, tuple) and len(color) == 3:
            self._check_rgb_range(color)
            fs_cmd.rgb.red, fs_cmd.rgb.green, fs_cmd.rgb.blue = color
        else:
            raise ValueError("Invalid color type")
        fs_cmd.blink = blink
        self._client.function_control_set(
            fs_cmd, Pb.FunctionControlSetResponse()
        )

    @connectable
    def get(self, channel: int) -> Tuple[int, int, int, bool]:
        """
        Get the state of a single channel.
        @param channel: channel number
        @return: LED color and blink state as a tuple (red, green, blue, blink)
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        """
        fs_cmd = Pb.FunctionControlGet()
        fs_cmd.channel = channel
        fs_response = Pb.FunctionControlGetResponse()
        self._client.function_control_get(fs_cmd, fs_response)
        return fs_response.rgb.red, fs_response.rgb.green, fs_response.rgb.blue, fs_response.blink

    def _check_rgb_range(self, color: Pb.RGBColor | Tuple[int, int, int]) -> None:
        if isinstance(color, Pb.RGBColor):
            for c in (color.red, color.green, color.blue):
                if not (0 <= c <= 255):
                    raise ValueError("RGB color values must be in the range 0-255")
        elif isinstance(color, tuple) and len(color) == 3:
            for c in color:
                if not (0 <= c <= 255):
                    raise ValueError("RGB color values must be in the range 0-255")
        else:
            raise ValueError("Invalid color type")
