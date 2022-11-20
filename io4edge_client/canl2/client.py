# SPDX-License-Identifer: Apache-2.0
from io4edge_client.functionblock import Client as FbClient
import io4edge_client.api.canL2.python.canL2.v1alpha1.canL2_pb2 as Pb
import io4edge_client.api.io4edge.python.functionblock.v1alpha1.io4edge_functionblock_pb2 as FbPb


class Client:
    def __init__(self, addr: str):
        self._fb_client = FbClient(addr + "._io4edge_canL2._tcp")

    def upload_configuration(self, config: Pb.ConfigurationSet):
        self._fb_client.upload_configuration(config)

    def download_configuration(self) -> Pb.ConfigurationGetResponse:
        fs_response = Pb.ConfigurationGetResponse()
        self._fb_client.download_configuration(fs_response)
        return fs_response

    def send_frames(self, frames: list[Pb.SendFrames]):
        fs_cmd = Pb.FunctionControlSet(frame=frames)
        self._fb_client.function_control_set(fs_cmd)

    def ctrl_state(self):
        fs_cmd = Pb.FunctionControlGet()
        fs_response = Pb.FunctionControlGetResponse()
        self._fb_client.function_control_get(fs_cmd, fs_response)
        return fs_response.controllerState

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
