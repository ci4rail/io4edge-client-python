# SPDX-License-Identifer: Apache-2.0
from io4edge_client.functionblock import Client as FbClient
import io4edge_client.api.colorLED.python.colorLED.v1alpha1.colorLED_pb2 as Pb


class Client:
    """
    colorLED functionblock client.
    @param addr: address of io4edge function block (mdns name or "ip:port" address)
    @param command_timeout: timeout for commands in seconds
    """

    def __init__(self, addr: str, command_timeout=5):
        self._fb_client = FbClient("_io4edge_colorLED._tcp", addr, command_timeout)

    def describe(self) -> Pb.ConfigurationDescribeResponse:
        """
        Get the description from the colorLED functionblock.
        @return: description from the colorLED functionblock
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        """
        fs_response = Pb.ConfigurationDescribeResponse()
        self._fb_client.describe(Pb.ConfigurationDescribe(), fs_response)
        return fs_response

    def set(self, channel: int, color: Pb.Color, blink: bool):
        """
        Set the state of a single output.
        @param color: color to set
        @param blink: if true the LED should blink
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        """
        fs_cmd = Pb.FunctionControlSet()
        fs_cmd.channel = channel
        fs_cmd.color = color
        fs_cmd.blink = blink
        self._fb_client.function_control_set(fs_cmd, Pb.FunctionControlSetResponse())

    def get(self, channel: int) -> tuple[Pb.Color, bool]:
        """
        Get the state of a single input.
        @param color: LED color
        @param blink: if true the LED is blinking
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        """
        fs_cmd = Pb.FunctionControlGet()
        fs_cmd.channel = channel
        fs_response = Pb.FunctionControlGetResponse()
        self._fb_client.function_control_get(fs_cmd, fs_response)
        return fs_response.color, fs_response.blink

    def close(self):
        """
        Close the connection to the function block, terminate read thread.
        After calling this method, the object is no longer usable.
        """
        self._fb_client.close()
