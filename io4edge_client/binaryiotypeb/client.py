# SPDX-License-Identifier: Apache-2.0
from io4edge_client.functionblock import Client as FbClient
import io4edge_client.api.binaryIoTypeB.python.binaryIoTypeB.v1alpha1.binaryIoTypeB_pb2 as Pb
import io4edge_client.api.io4edge.python.functionblock.v1alpha1.io4edge_functionblock_pb2 as FbPb


class Client:
    """
    binaryIoTypeB functionblock client.
    @param addr: address of io4edge function block (mdns name or "ip:port" address)
    @param command_timeout: timeout for commands in seconds
    """

    def __init__(self, addr: str, command_timeout=5, connect=True):
        self._fb_client = FbClient("_io4edge_binaryIoTypeB._tcp", addr, command_timeout, connect=connect)

    def describe(self) -> Pb.ConfigurationDescribeResponse:
        """
        Get the description from the binaryIoTypeB functionblock.
        @return: description from the binaryIoTypeB functionblock
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        """
        fs_response = Pb.ConfigurationDescribeResponse()
        if self._fb_client.connected:
            self._fb_client.describe(Pb.ConfigurationDescribe(), fs_response)
        else:
            with self._fb_client as fb:
                fb.describe(Pb.ConfigurationDescribe(), fs_response)
        return fs_response

    def set_output(self, channel: int, state: bool):
        """
        Set the state of a single output.
        @param channel: channel number
        @param state: state to set. a "true" state turns on the outputs switch, a "false" state turns it off.
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        """
        fs_cmd = Pb.FunctionControlSet()
        fs_cmd.single.channel = channel
        fs_cmd.single.state = state
        if self._fb_client.connected:
            self._fb_client.function_control_set(fs_cmd, Pb.FunctionControlSetResponse())
        else:
            with self._fb_client as fb:
                fb.function_control_set(fs_cmd, Pb.FunctionControlSetResponse())

    def set_all_outputs(self, states: int, mask: int):
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
        if self._fb_client.connected:
            self._fb_client.function_control_set(fs_cmd, Pb.FunctionControlSetResponse())
        else:
            with self._fb_client as fb:
                fb.function_control_set(fs_cmd, Pb.FunctionControlSetResponse())

    def get_input(self, channel: int) -> bool:
        """
        Get the state of a single input.
        @param channel: channel number
        @return: state of the input
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        """
        fs_cmd = Pb.FunctionControlGet()
        fs_cmd.single.channel = channel
        fs_response = Pb.FunctionControlGetResponse()
        if self._fb_client.connected:
            self._fb_client.function_control_get(fs_cmd, fs_response)
        else:
            with self._fb_client as fb:
                fb.function_control_get(fs_cmd, fs_response)
        return fs_response.single.state

    def get_all_inputs(self) -> int:
        """
        Get the state of all inputs.
        @return: binary coded map of inputs. 0 means switch off, 1 means switch on, LSB is Channel0
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        """
        fs_cmd = Pb.FunctionControlGet()
        fs_response = Pb.FunctionControlGetResponse()
        if self._fb_client.connected:
            self._fb_client.function_control_get(fs_cmd, fs_response)
        else:
            with self._fb_client as fb:
                fb.function_control_get(fs_cmd, fs_response)
        return fs_response.all.values

    def close(self):
        """
        Close the connection to the function block, terminate read thread.
        After calling this method, the object is no longer usable.
        """
        self._fb_client.close()

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
