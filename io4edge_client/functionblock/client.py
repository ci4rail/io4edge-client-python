from io4edge_client.base import Client as BaseClient
import io4edge_client.api.io4edge.python.functionblock.v1alpha1.io4edge_functionblock_pb2 as FbPb

class Client:
    def __init__(self, addr: str):
        self._client = BaseClient(addr)

    def function_control_set(self, fs_cmd):
        any = 

        fc = FbPb.FunctionControl()
        fc.functionSpecificFunctionControlSet 

        cmd = FbPb.Command()
        cmd.function_control = fc


    def _command(self, cmd: FbPb.Command):
        self._client.write_msg(cmd)
        response = FbPb.Response()
        self._client.read_msg(response)
        return response

    def close(self):
        self._client.close()

