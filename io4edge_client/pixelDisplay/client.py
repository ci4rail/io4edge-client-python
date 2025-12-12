# SPDX-License-Identifier: Apache-2.0
import zlib
from typing import List, Tuple
from io4edge_client.base.connections import ClientConnection, connectable
from io4edge_client.base.logging import io4edge_client_logger
from io4edge_client.functionblock import Client as FbClient
import io4edge_client.api.pixelDisplay.python.pixelDisplay.v1alpha1.pixelDisplay_pb2 as Pb  # noqa: E501


class Client(ClientConnection):
    """
    pixelDisplay functionblock client.
    @param addr: address of io4edge function block (mdns name or "ip:port" address)
    @param command_timeout: timeout for commands in seconds
    """

    def __init__(
        self,
        addr: str,
        command_timeout: int = 5,
        connect: bool = True
    ) -> None:
        self._logger = io4edge_client_logger("pixelDisplay.Client")
        self._logger.debug("Initializing pixelDisplay client")
        fb_client = FbClient(
            "_io4edge_pixelDisplay._tcp", addr, command_timeout,
            connect=connect
        )
        super().__init__(fb_client)
        # Type hint for better IDE support
        self._client: FbClient = self._client

    @connectable
    def describe(self) -> Pb.ConfigurationDescribeResponse:
        """
        Get the description from the pixelDisplay functionblock.
        @return: description from the pixelDisplay functionblock
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        """
        fs_response = Pb.ConfigurationDescribeResponse()
        self._client.describe(Pb.ConfigurationDescribe(), fs_response)
        return fs_response

    @connectable
    def set_pixel_area(
        self,
        startx: int,
        starty: int,
        endx: int,
        pixel_area: List[Tuple[int, int, int]]
    ) -> None:
        """
        Set the pixel area of the display.
        @param startx: starting x-coordinate of the pixel area
        @param starty: starting y-coordinate of the pixel area
        @param endx: ending x-coordinate of the pixel area
        @param pixel_area: list of RGB tuples representing the pixel colors
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        """
        fs_cmd = Pb.FunctionControlSet()
        pixel = bytearray(len(pixel_area) * 3)
        for i in range(len(pixel_area)):
            pixel[i * 3 + 0] = pixel_area[i][0]
            pixel[i * 3 + 1] = pixel_area[i][1]
            pixel[i * 3 + 2] = pixel_area[i][2]
        fs_cmd.set_pixel_area.start_x = startx
        fs_cmd.set_pixel_area.start_y = starty
        fs_cmd.set_pixel_area.end_x = endx
        # compress pixel before sending to the function block
        fs_cmd.set_pixel_area.image = zlib.compress(pixel)
        self._client.function_control_set(
            fs_cmd, Pb.FunctionControlSetResponse()
        )

    @connectable
    def set_display_off(self) -> None:
        """
        Turn off the display.
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        """
        fs_cmd = Pb.FunctionControlSet()
        fs_cmd.display_on.on = False
        self._client.function_control_set(
            fs_cmd, Pb.FunctionControlSetResponse()
        )
