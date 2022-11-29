# SPDX-License-Identifer: Apache-2.0
from io4edge_client.functionblock import Client as FbClient
import io4edge_client.api.binaryIoTypeC.python.binaryIoTypeC.v1alpha1.binaryIoTypeC_pb2 as Pb
import io4edge_client.api.io4edge.python.functionblock.v1alpha1.io4edge_functionblock_pb2 as FbPb


class Client:
    """
    binaryIoTypeC functionblock client.
    @param addr: address of io4edge function block (mdns name or "ip:port" address)
    @param command_timeout: timeout for commands in seconds
    """

    def __init__(self, addr: str, command_timeout=5):
        self._fb_client = FbClient("_io4edge_binaryIoTypeC._tcp", addr, command_timeout)

    def upload_configuration(self, config: Pb.ConfigurationSet):
        """
        Upload the configuration to the binaryIoTypeC functionblock.
        @param config: configuration to upload
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        """
        self._fb_client.upload_configuration(config)

    def download_configuration(self) -> Pb.ConfigurationGetResponse:
        """
        Download the configuration from the binaryIoTypeC functionblock.
        @return: actual configuration
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        """
        fs_response = Pb.ConfigurationGetResponse()
        self._fb_client.download_configuration(Pb.ConfigurationGet(), fs_response)
        return fs_response

    def describe(self) -> Pb.ConfigurationDescribeResponse:
        """
        Get the description from the binaryIoTypeC functionblock.
        @return: description from the binaryIoTypeC functionblock
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        """
        fs_response = Pb.ConfigurationDescribeResponse()
        self._fb_client.describe(Pb.ConfigurationDescribe(), fs_response)
        return fs_response

    def set_output(self, channel: int, state: bool):
        """
        Set the state of a single output.
        @param channel: channel number
        @param state: state to set. a "true" state sets the output to high, a "false" state sets the output to low
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        """
        fs_cmd = Pb.FunctionControlSet()
        fs_cmd.single.channel = channel
        fs_cmd.single.state = state
        self._fb_client.function_control_set(fs_cmd, Pb.FunctionControlSetResponse())

    def set_all_outputs(self, states: int, mask: int):
        """
        Set the state of all or a group of output channels.
        @param states: binary coded map of outputs. 0 means switch low, 1 means switch high, LSB is Channel0
        @param mask: binary coded map of outputs to be set. 0 means do not change, 1 means change, LSB is Channel0
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        """
        fs_cmd = Pb.FunctionControlSet()
        fs_cmd.all.states = states
        fs_cmd.all.mask = mask
        self._fb_client.function_control_set(fs_cmd, Pb.FunctionControlSetResponse())

    def input(self, channel: int):
        """
        Get the state of a single channel, regardless whether its configured as input or output)
        and the diagnostic info of a single channel.
        State "true" state means the input is high, a "false" state means the input is low.
        The returned diagnostic info is a bitfield containing diagnostic bits.
        @param channel: channel number
        @return: state of the input, diagnostic info.
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        """
        fs_cmd = Pb.FunctionControlGet()
        fs_cmd.single.channel = channel
        fs_response = Pb.FunctionControlGetResponse()
        self._fb_client.function_control_get(fs_cmd, fs_response)
        return fs_response.single.state, fs_response.single.diag

    def all_inputs(self) -> Pb.FunctionControlGetResponse:
        """
        Get the state of all channels, regardless whether they are configured as input or output.
        Each bit in the returned state corresponds to one channel, bit0 being channel 0.
        The bit is false if the pin level is low, true otherwise.
        diag is a slice with bitfields containing diagnostic bits for each channel.
        """
        fs_cmd = Pb.FunctionControlGet()
        fs_cmd.all.CopyFrom(Pb.GetAll())
        fs_response = Pb.FunctionControlGetResponse()
        self._fb_client.function_control_get(fs_cmd, fs_response)
        return fs_response.all

    def start_stream(
        self, config: Pb.StreamControlStart, fb_config: FbPb.StreamControl
    ):
        """
        Start streaming of transitions.
        @param config: filter configuration of the stream
        @param fb_config: functionblock generic configuration of the stream
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        """
        self._fb_client.start_stream(config, fb_config)

    def stop_stream(self):
        """
        Stop streaming of transitions.
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        """
        self._fb_client.stop_stream()

    def read_stream(self, timeout=None):
        """
        Read the next message from the stream.
        @param timeout: timeout in seconds
        @return: functionblock generic stream data (deliveryTimestampUs, sequence), binaryIoTypeC specific stream data
        @raises TimeoutError: if no data is available within the timeout
        """
        stream_data = Pb.StreamData()
        generic_stream_data = self._fb_client.read_stream(timeout, stream_data)
        return generic_stream_data, stream_data

    def close(self):
        """
        Close the connection to the function block, terminate read thread.
        After calling this method, the object is no longer usable.
        """
        self._fb_client.close()
