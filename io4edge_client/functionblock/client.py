from io4edge_client.base import Client as BaseClient
import io4edge_client.api.io4edge.python.functionblock.v1alpha1.io4edge_functionblock_pb2 as FbPb
import google.protobuf.any_pb2 as AnyPb


class Client:
    def __init__(self, addr: str):
        self._client = BaseClient(addr)

    def function_control_set(self, fs_cmd):
        fs_any = AnyPb.Any()
        fs_any.Pack(fs_cmd)

        fb_cmd = FbPb.Command()
        fb_cmd.functionControl.functionSpecificFunctionControlSet.CopyFrom(fs_any)
        fb_res = self._command(fb_cmd)
        return fb_res.functionControl.functionSpecificFunctionControlSet

    def _command(self, cmd: FbPb.Command):
        self._client.write_msg(cmd)
        response = FbPb.Response()
        self._client.read_msg(response)
        if response.status != FbPb.Status.OK:
            raise RuntimeError(f"Command failed: {response.status}: {response.error}")
        return response

    def close(self):
        self._client.close()
