from io4edge_client.functionblock.client import Client as FbClient
import io4edge_client.api.binaryIoTypeC.python.binaryIoTypeC.v1alpha1.binaryIoTypeC_pb2 as BinIoPb


class Client:
    def __init__(self, addr: str):
        self._fb_client = FbClient(addr)

    def set_output(self, channel: int, state: bool):
        fs_cmd = BinIoPb.FunctionControlSet()
        fs_cmd.single.channel = channel
        fs_cmd.single.state = state
        self._fb_client.function_control_set(fs_cmd)
