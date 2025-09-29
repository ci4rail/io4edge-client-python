# SPDX-License-Identifier: Apache-2.0
from io4edge_client.functionblock import Client as FbClient
import io4edge_client.api.binaryIoTypeD.python.binaryIoTypeD.v1.binaryIoTypeD_pb2 as Pb
import io4edge_client.api.io4edge.python.functionblock.v1alpha1.io4edge_functionblock_pb2 as FbPb


class Client:
    """
    binaryIoTypeD functionblock client.
    @param addr: address of io4edge function block (mdns name or "ip:port" address)
    @param command_timeout: timeout for commands in seconds
    """

    def __init__(self, addr: str, command_timeout=5, connect=True):
        self._fb_client = FbClient("_io4edge_binaryIoTypeD._tcp", addr, command_timeout, connect=connect)

    def upload_configuration(self, config: Pb.ConfigurationSet):
        """
        Upload the configuration to the binaryIoTypeD functionblock.
        @param config: configuration to upload
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        """
        self._fb_client.upload_configuration(config)

    def download_configuration(self) -> Pb.ConfigurationGetResponse:
        """
        Download the configuration from the binaryIoTypeD functionblock.
        @return: actual configuration
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        """
        fs_response = Pb.ConfigurationGetResponse()
        self._fb_client.download_configuration(Pb.ConfigurationGet(), fs_response)
        return fs_response

    def set_output(self, channel: int, state: bool):
        """
        Set the state of a single output.
        @param channel: channel number
        @param state: state to set. a "true" state turns on the output switch, a "false" state turns it off.
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        """
        fs_cmd = Pb.FunctionControlSet()
        fs_cmd.single.channel = channel
        fs_cmd.single.state = state
        self._fb_client.function_control_set(fs_cmd, Pb.FunctionControlSetResponse())

    def set_outputs(self, states: int, mask: int):
        """
        Set the state of all or a group of output channels.
        @param states: binary coded map of outputs. 0 means switch off, 1 means switch on, LSB is Channel0
        @param mask: binary coded map of outputs to be set. 0 means do not change, 1 means change, LSB is Channel0
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        """
        fs_cmd = Pb.FunctionControlSet()
        fs_cmd.all.values = states
        fs_cmd.all.mask = mask
        self._fb_client.function_control_set(fs_cmd, Pb.FunctionControlSetResponse())

    def get_channels(self) -> Pb.FunctionControlGetResponse:
        """
        Get the state of all channels, regardless whether they are configured as input or output.
        Each bit in the returned "inputs" corresponds to one channel, bit0 being channel 0.
        The bit is false if the pin level is inactive, or true if active.
        diag is a slice with bitfields containing diagnostic bits for each channel.
        @return: state of all inputs plus diagnostic info
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        """
        fs_cmd = Pb.FunctionControlGet()
        fs_response = Pb.FunctionControlGetResponse()
        self._fb_client.function_control_get(fs_cmd, fs_response)
        return fs_response

    def close(self):
        """
        Close the connection to the function block, terminate read thread.
        After calling this method, the object is no longer usable.
        """
        self._fb_client.close()
