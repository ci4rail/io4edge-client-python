import threading
from collections import deque
from io4edge_client.base import Client as BaseClient
import io4edge_client.api.io4edge.python.functionblock.v1alpha1.io4edge_functionblock_pb2 as FbPb
import google.protobuf.any_pb2 as AnyPb


class Client:
    def __init__(self, addr: str, command_timeout=5):
        self._client = BaseClient(addr)
        self._stream_queue_mutex = (
            threading.Lock()
        )  # Protects _stream_queue from concurrent access
        self._stream_queue_sema = threading.Semaphore(0)  # count items in _stream_queue
        self._stream_queue = deque()
        self._cmd_event = threading.Event()
        self._cmd_mutex = (
            threading.Lock()
        )  # Ensures only one command is pending at a time
        self._cmd_response = None
        self._cmd_context = 0  # sequence number for command context
        self._cmd_timeout = command_timeout
        self._read_thread_stop = False
        self._read_thread_id = threading.Thread(target=self._read_thread, daemon=True)
        self._read_thread_id.start()

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

    def start_stream(self, fs_config, fb_config: FbPb.StreamControlStart):
        fs_any = AnyPb.Any()
        fs_any.Pack(fs_config)

        fb_config.functionSpecificStreamControlStart.CopyFrom(fs_any)
        fb_cmd = FbPb.Command()
        fb_cmd.streamControl.start.CopyFrom(fb_config)

        self._command(fb_cmd)

    def stop_stream(self):
        fb_cmd = FbPb.Command()
        fb_cmd.streamControlStop = FbPb.StreamControlStop()
        self._command(fb_cmd)

    def read_stream(self, timeout, stream_data):
        self._stream_queue_sema.acquire(timeout=timeout)
        with self._stream_queue_mutex:
            data = self._stream_queue.popleft()
            fs_any = AnyPb.Any()
            fs_any.CopyFrom(data.functionSpecificStreamData)
            if not fs_any.type_url.startswith("type.googleapis.com/"):
                fs_any.type_url = "type.googleapis.com/" + fs_any.type_url
            fs_any.Unpack(stream_data)
            return data

    def _command(self, cmd: FbPb.Command):
        with self._cmd_mutex:
            cmd.context.value = str(self._cmd_context)
            self._cmd_event.clear()
            self._client.write_msg(cmd)
            if not self._cmd_event.wait(timeout=self._cmd_timeout):
                raise RuntimeError("Command timed out")

            response = self._cmd_response
            if response.context.value != str(self._cmd_context):
                raise RuntimeError(f"Command context mismatch. Got {response.context.value}, expected {self._cmd_context}")

            self._cmd_context += 1

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
        self._stream_queue_sema.release()

    def close(self):
        self._read_thread_stop = True
        self._read_thread_id.join()
        self._client.close()
