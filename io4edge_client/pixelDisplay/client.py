# SPDX-License-Identifier: Apache-2.0
from io4edge_client.functionblock import Client as FbClient
import io4edge_client.api.pixelDisplay.python.pixelDisplay.v1alpha1.pixelDisplay_pb2 as Pb
import io4edge_client.api.io4edge.python.functionblock.v1alpha1.io4edge_functionblock_pb2 as FbPb
import time
import zlib
import sys


class Client:
    """
    pixelDisplay functionblock client.
    @param addr: address of io4edge function block (mdns name or "ip:port" address)
    @param command_timeout: timeout for commands in seconds
    """

    def __init__(self, addr: str, command_timeout=5, connect=True):
        self._fb_client = FbClient("_io4edge_pixelDisplay._tcp", addr, command_timeout, connect=connect)

    def describe(self) -> Pb.ConfigurationDescribeResponse:
        """
        Get the description from the pixelDisplay functionblock.
        @return: description from the pixelDisplay functionblock
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        """
        fs_response = Pb.ConfigurationDescribeResponse()
        self._fb_client.describe(Pb.ConfigurationDescribe(), fs_response)
        return fs_response

    def set_pixel_area(self, startx: int, starty: int, endx: int, pixel_area: list):
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
        self._fb_client.function_control_set(fs_cmd, Pb.FunctionControlSetResponse())

    def set_display_off(self):
        """
        Set the state of all or a group of output channels.
        @param states: binary coded map of outputs. 0 means switch off, 1 means switch on, LSB is Channel0
        @param mask: binary coded map of outputs to be set. 0 means do not change, 1 means change, LSB is Channel0
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        """
        fs_cmd = Pb.FunctionControlSet()
        fs_cmd.display_on.on = False
        self._fb_client.function_control_set(fs_cmd, Pb.FunctionControlSetResponse())

    def close(self):
        """
        Close the connection to the function block, terminate read thread.
        After calling this method, the object is no longer usable.
        """
        self._fb_client.close()
