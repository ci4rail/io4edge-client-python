# SPDX-License-Identifer: Apache-2.0
from io4edge_client.functionblock import Client as FbClient
import io4edge_client.api.binaryIoTypeC.python.binaryIoTypeC.v1alpha1.binaryIoTypeC_pb2 as Pb
import io4edge_client.api.io4edge.python.functionblock.v1alpha1.io4edge_functionblock_pb2 as FbPb


class Client:
    def __init__(self, addr: str, command_timeout=5):
        self._fb_client = FbClient(addr, "_io4edge_binaryIoTypeC._tcp", command_timeout)

    def upload_configuration(self, config: Pb.ConfigurationSet):
        self._fb_client.upload_configuration(config)

    def download_configuration(self) -> Pb.ConfigurationGetResponse:
        fs_response = Pb.ConfigurationGetResponse()
        self._fb_client.download_configuration(Pb.ConfigurationGet(), fs_response)
        return fs_response

    def describe(self):
        fs_response = Pb.ConfigurationDescribeResponse()
        self._fb_client.describe(Pb.ConfigurationDescribe(), fs_response)
        return fs_response

    def set_output(self, channel: int, state: bool):
        fs_cmd = Pb.FunctionControlSet()
        fs_cmd.single.channel = channel
        fs_cmd.single.state = state
        self._fb_client.function_control_set(fs_cmd, Pb.FunctionControlSetResponse())

    def set_all_outputs(self, states: int, mask: int):
        fs_cmd = Pb.FunctionControlSet()
        fs_cmd.all.states = states
        fs_cmd.all.mask = mask
        self._fb_client.function_control_set(fs_cmd, Pb.FunctionControlSetResponse())

    def input(self, channel: int):
        fs_cmd = Pb.FunctionControlGet()
        fs_cmd.single.channel = channel
        fs_response = Pb.FunctionControlGetResponse()
        self._fb_client.function_control_get(fs_cmd, fs_response)
        return fs_response.single.state, fs_response.single.diag

    def all_inputs(self):
        fs_cmd = Pb.FunctionControlGet()
        fs_cmd.all.CopyFrom(Pb.GetAll())
        fs_response = Pb.FunctionControlGetResponse()
        self._fb_client.function_control_get(fs_cmd, fs_response)
        return fs_response.all

    def start_stream(
        self, config: Pb.StreamControlStart, fb_config: FbPb.StreamControl
    ):
        self._fb_client.start_stream(config, fb_config)

    def stop_stream(self):
        self._fb_client.stop_stream()

    def read_stream(self, timeout=None):
        stream_data = Pb.StreamData()
        generic_stream_data = self._fb_client.read_stream(timeout, stream_data)
        return generic_stream_data, stream_data

    def close(self):
        self._fb_client.close()
