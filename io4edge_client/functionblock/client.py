import threading
from collections import deque
from io4edge_client.base import Client as BaseClient
import io4edge_client.api.io4edge.python.functionblock.v1alpha1.io4edge_functionblock_pb2 as FbPb
import google.protobuf.any_pb2 as AnyPb


class Client:
    def __init__(self, addr: str, command_timeout=5):
        self._client = BaseClient(addr)
        self._stream_queue_mutex = threading.Lock()
        self._stream_queue = deque()
        self._cmd_event = threading.Event()
        self._cmd_mutex = threading.Lock()
        self._cmd_response = None
        self._cmd_timeout = command_timeout
        self._read_thread_id = threading.Thread(target=self._read_thread, daemon=True)
        self._read_thread_id.start()
        self._read_thread_stop = False

    def upload_configuration(self, fs_cmd):
        fs_any = AnyPb.Any()
        fs_any.Pack(fs_cmd)

        fb_cmd = FbPb.Command()
        fb_cmd.Configuration.functionSpecificConfigurationSet.CopyFrom(fs_any)
        fb_res = self._command(fb_cmd)
        return fb_res.Configuration.functionSpecificConfigurationSet

    def download_configuration(self, fs_cmd):
        fs_any = AnyPb.Any()
        fs_any.Pack(fs_cmd)

        fb_cmd = FbPb.Command()
        fb_cmd.Configuration.functionSpecificConfigurationGet.CopyFrom(fs_any)
        fb_res = self._command(fb_cmd)
        return fb_res.Configuration.functionSpecificConfigurationGet

    def describe(self, fs_cmd):
        fs_any = AnyPb.Any()
        fs_any.Pack(fs_cmd)

        fb_cmd = FbPb.Command()
        fb_cmd.Configuration.functionSpecificConfigurationDescribe.CopyFrom(fs_any)
        fb_res = self._command(fb_cmd)
        return fb_res.Configuration.functionSpecificConfigurationDescribe

    def function_control_set(self, fs_cmd):
        fs_any = AnyPb.Any()
        fs_any.Pack(fs_cmd)

        fb_cmd = FbPb.Command()
        fb_cmd.functionControl.functionSpecificFunctionControlSet.CopyFrom(fs_any)
        fb_res = self._command(fb_cmd)
        return fb_res.functionControl.functionSpecificFunctionControlSet

    def function_control_get(self, fs_cmd):
        fs_any = AnyPb.Any()
        fs_any.Pack(fs_cmd)

        fb_cmd = FbPb.Command()
        fb_cmd.functionControl.functionSpecificFunctionControlGet.CopyFrom(fs_any)
        fb_res = self._command(fb_cmd)
        return fb_res.functionControl.functionSpecificFunctionControlGet

    def _command(self, cmd: FbPb.Command):
        with self._cmd_mutex:
            self._cmd_event.clear()
            self._client.write_msg(cmd)
            if not self._cmd_event.wait(timeout=self._cmd_timeout):
                raise RuntimeError("Command timed out")

            response = self._cmd_response
            if response.status != FbPb.Status.OK:
                raise RuntimeError(
                    f"Command failed: {response.status}: {response.error}"
                )
            return response

    def _read_thread(self):
        print("Read thread started")
        while not self._read_thread_stop:
            msg = FbPb.Response()
            try:
                self._client.read_msg(msg, timeout=1)
            except TimeoutError:
                continue

            if msg.WhichOneof("type") == "stream":
                self._feed_stream(msg.stream)
            else:
                self._cmd_response = msg
                self._cmd_event.set()
        print("Read thread stopped")

    def _feed_stream(self, stream_data):
        with self._stream_queue_mutex:
            self._stream_queue.append(stream_data)

    def close(self):
        self._read_thread_stop = True
        self._read_thread_id.join()
        self._client.close()
