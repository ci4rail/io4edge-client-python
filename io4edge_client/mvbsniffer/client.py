# SPDX-License-Identifer: Apache-2.0
from io4edge_client.functionblock import Client as FbClient
import io4edge_client.api.mvbSniffer.python.mvbSniffer.v1.mvbSniffer_pb2 as Pb  # noqa: F401
import io4edge_client.api.mvbSniffer.python.mvbSniffer.v1.telegram_pb2 as TelegramPb  # noqa: F401
import io4edge_client.api.io4edge.python.functionblock.v1alpha1.io4edge_functionblock_pb2 as FbPb


class Client:
    def __init__(self, addr: str):
        self._fb_client = FbClient(addr + "._io4edge_mvbSniffer._tcp")

    def send_pattern(self, msg: str):
        fs_cmd = Pb.FunctionControlSet(GeneratorPattern=msg)
        self._fb_client.function_control_set(fs_cmd)

    def start_stream(
        self, config: Pb.StreamControlStart, fb_config: FbPb.StreamControl
    ):
        self._fb_client.start_stream(config, fb_config)

    def stop_stream(self):
        self._fb_client.stop_stream()

    def read_stream(self, timeout=None):
        stream_data = TelegramPb.TelegramCollection()
        generic_stream_data = self._fb_client.read_stream(timeout, stream_data)
        return generic_stream_data, stream_data

    def close(self):
        self._fb_client.close()
