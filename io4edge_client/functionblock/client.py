# SPDX-License-Identifer: Apache-2.0
import threading
from collections import deque
from io4edge_client.base import Client as BaseClient
from ..util.any import pb_any_unpack
import io4edge_client.api.io4edge.python.functionblock.v1alpha1.io4edge_functionblock_pb2 as FbPb
import google.protobuf.any_pb2 as AnyPb


class Client:
    """
    io4edge functionblock client.
    @param addr: address of io4edge function block (mdns name or "ip:port" address)
    @param service: service name of io4edge function block
    @param command_timeout: timeout for commands in seconds
    """

    def __init__(self, addr: str, service: str, command_timeout=5):
        self._client = BaseClient(addr, service)
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
        """
        Upload configuration to io4edge function block.
        @param fs_cmd: protobuf message with the function specific configuration
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        """
        fs_any = AnyPb.Any()
        fs_any.Pack(fs_cmd)

        fb_cmd = FbPb.Command()
        fb_cmd.Configuration.functionSpecificConfigurationSet.CopyFrom(fs_any)
        self._command(fb_cmd)

    def download_configuration(self, fs_cmd, fs_response):
        """
        Download configuration from io4edge function block.
        @param fs_cmd: protobuf message with the function specific configuration (mostly empty)
        @param fs_response: protobuf message that is filled with the function specific configuration response
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        """
        fs_any = AnyPb.Any()
        fs_any.Pack(fs_cmd)

        fb_cmd = FbPb.Command()
        fb_cmd.Configuration.functionSpecificConfigurationGet.CopyFrom(fs_any)
        fb_res = self._command(fb_cmd)
        pb_any_unpack(
            fb_res.Configuration.functionSpecificConfigurationGet, fs_response
        )

    def describe(self, fs_cmd, fs_response):
        """
        Describe the function block (call the firmware describe function).
        @param fs_cmd: protobuf message with the function specific describe request (mostly empty)
        @param fs_response: protobuf message that is filled with the function specific describe response
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        """
        fs_any = AnyPb.Any()
        fs_any.Pack(fs_cmd)

        fb_cmd = FbPb.Command()
        fb_cmd.Configuration.functionSpecificConfigurationDescribe.CopyFrom(fs_any)
        fb_res = self._command(fb_cmd)
        pb_any_unpack(
            fb_res.Configuration.functionSpecificConfigurationDescribe, fs_response
        )

    def function_control_set(self, fs_cmd, fs_response):
        """
        Execute "function control set" command on io4edge function block.
        @param fs_cmd: protobuf message with the function specific function control set request
        @param fs_response: protobuf message that is filled with the function specific function control set response
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        """
        fs_any = AnyPb.Any()
        fs_any.Pack(fs_cmd)

        fb_cmd = FbPb.Command()
        fb_cmd.functionControl.functionSpecificFunctionControlSet.CopyFrom(fs_any)
        fb_res = self._command(fb_cmd)
        pb_any_unpack(
            fb_res.functionControl.functionSpecificFunctionControlSet, fs_response
        )

    def function_control_get(self, fs_cmd, fs_response):
        """
        Execute "function control get" command on io4edge function block.
        @param fs_cmd: protobuf message with the function specific function control get request (mostly empty)
        @param fs_response: protobuf message that is filled with the function specific function control get response
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        """
        fs_any = AnyPb.Any()
        fs_any.Pack(fs_cmd)

        fb_cmd = FbPb.Command()
        fb_cmd.functionControl.functionSpecificFunctionControlGet.CopyFrom(fs_any)
        fb_res = self._command(fb_cmd)
        pb_any_unpack(
            fb_res.functionControl.functionSpecificFunctionControlGet, fs_response
        )

    def start_stream(self, fs_config, fb_config: FbPb.StreamControlStart):
        """
        Start streaming data from io4edge function block.
        @param fs_config: protobuf message with the function specific configuration
        @param fb_config: protobuf message with the function block configuration
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        """
        fs_any = AnyPb.Any()
        fs_any.Pack(fs_config)

        fb_config.functionSpecificStreamControlStart.CopyFrom(fs_any)
        fb_cmd = FbPb.Command()
        fb_cmd.streamControl.start.CopyFrom(fb_config)

        self._command(fb_cmd)

    def stop_stream(self):
        """
        Stop streaming data from io4edge function block.
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        """
        fb_cmd = FbPb.Command()
        stop = FbPb.StreamControlStop()
        fb_cmd.streamControl.stop.CopyFrom(stop)
        self._command(fb_cmd)

    def read_stream(self, timeout, stream_data):
        """
        Read next message from stream.
        @param timeout: timeout in seconds
        @param stream_data: protobuf message that is filled with the stream data
        @return functionblock stream meta data (deliveryTimestampUs, sequence)
        @raises TimeoutError: if no data is available within the timeout
        """
        self._stream_queue_sema.acquire(timeout=timeout)
        with self._stream_queue_mutex:
            data = self._stream_queue.popleft()
            pb_any_unpack(data.functionSpecificStreamData, stream_data)
            return data

    def _command(self, cmd: FbPb.Command):
        with self._cmd_mutex:
            cmd.context.value = str(self._cmd_context)
            self._cmd_event.clear()
            self._client.write_msg(cmd)
            if not self._cmd_event.wait(timeout=self._cmd_timeout):
                raise TimeoutError("Command timed out")

            response = self._cmd_response
            if response.context.value != str(self._cmd_context):
                raise RuntimeError(
                    f"Command context mismatch. Got {response.context.value}, expected {self._cmd_context}"
                )

            self._cmd_context += 1

            if response.status != FbPb.Status.OK:
                status_str = FbPb.Status.Name(response.status)
                raise RuntimeError(
                    f"Command failed: {status_str}: {response.error}"
                )
            return response

    def _read_thread(self):
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

    def _feed_stream(self, stream_data):
        with self._stream_queue_mutex:
            self._stream_queue.append(stream_data)
        self._stream_queue_sema.release()

    def close(self):
        """
        Close the connection to the function block, terminate read thread.
        After calling this method, the object is no longer usable.
        """
        self._read_thread_stop = True
        self._read_thread_id.join()
        self._client.close()
