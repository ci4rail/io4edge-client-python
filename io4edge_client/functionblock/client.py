# SPDX-License-Identifier: Apache-2.0
import threading
from collections import deque
from io4edge_client.base import Client as BaseClient
from io4edge_client.base.connections import ClientConnection, connectable
from io4edge_client.base.logging import io4edge_client_logger
from io4edge_client.util.exceptions import CommandTemporaryUnavailableError
from ..util.any import pb_any_unpack
import io4edge_client.api.io4edge.python.functionblock.v1alpha1.io4edge_functionblock_pb2 as FbPb
import google.protobuf.any_pb2 as AnyPb


logger = io4edge_client_logger(__name__)


class Client(ClientConnection):
    """
    io4edge functionblock client.
    @param addr: address of io4edge function block (mdns name or "ip:port" address)
    @param service: service name of io4edge function block
    @param command_timeout: timeout for commands in seconds
    """

    def __init__(self, service: str, addr: str, command_timeout=5, connect=True):
        self._logger = io4edge_client_logger("functionblock.Client")
        self._logger.debug(f"Initializing functionblock client for "
                           f"service='{service}', addr='{addr}', "
                           f"timeout={command_timeout}")
        super().__init__(BaseClient(service, addr, connect=connect))
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
        self._read_thread_stop = True
        if connect:
            self.open()

    def open(self):
        self._logger.debug("Opening functionblock client connection")
        if not self.connected:
            self._client.open()
            self._read_thread_stop = False
            self._read_thread_id = threading.Thread(
                target=self._read_thread, daemon=True
            )
            self._read_thread_id.start()
            self._logger.debug("Functionblock client connection opened and "
                              "read thread started")

    @property
    def connected(self):
        return self._client.connected and not self._read_thread_stop

    def close(self):
        """
        Close the connection to the function block, terminate read thread.
        After calling this method, the object is no longer usable.
        """
        self._logger.debug("Closing functionblock client connection")
        self._read_thread_stop = True
        self._client.close()  # This closes the socket, which will interrupt the read
        self._read_thread_id.join()  # Thread should exit when socket operations fail
        self._logger.debug("Functionblock client connection closed")

    @connectable
    def upload_configuration(self, fs_cmd):
        """
        Upload configuration to io4edge function block.
        @param fs_cmd: protobuf message with the function specific configuration
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        """
        self._logger.debug("Uploading configuration to functionblock")
        fs_any = AnyPb.Any()
        fs_any.Pack(fs_cmd)

        fb_cmd = FbPb.Command()
        fb_cmd.Configuration.functionSpecificConfigurationSet.CopyFrom(fs_any)
        self._command(fb_cmd)
        self._logger.info("Configuration uploaded successfully")

    @connectable
    def download_configuration(self, fs_cmd, fs_response):
        """
        Download configuration from io4edge function block.
        @param fs_cmd: protobuf message with the function specific configuration (mostly empty)
        @param fs_response: protobuf message that is filled with the function specific configuration response
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        """
        self._logger.debug("Downloading configuration from functionblock")
        fs_any = AnyPb.Any()
        fs_any.Pack(fs_cmd)

        fb_cmd = FbPb.Command()
        fb_cmd.Configuration.functionSpecificConfigurationGet.CopyFrom(fs_any)
        fb_res = self._command(fb_cmd)
        pb_any_unpack(
            fb_res.Configuration.functionSpecificConfigurationGet, fs_response
        )
        self._logger.info("Configuration downloaded successfully")

    @connectable
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

    @connectable
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

    @connectable
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
        self._logger.debug("Starting stream from functionblock")
        fs_any = AnyPb.Any()
        fs_any.Pack(fs_config)

        fb_config.functionSpecificStreamControlStart.CopyFrom(fs_any)
        fb_cmd = FbPb.Command()
        fb_cmd.streamControl.start.CopyFrom(fb_config)

        self._command(fb_cmd)
        self._logger.info("Stream started successfully")

    def stop_stream(self):
        """
        Stop streaming data from io4edge function block.
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        """
        self._logger.debug("Stopping stream from functionblock")
        fb_cmd = FbPb.Command()
        stop = FbPb.StreamControlStop()
        fb_cmd.streamControl.stop.CopyFrom(stop)
        self._command(fb_cmd)
        self._logger.info("Stream stopped successfully")

    def read_stream(self, timeout, stream_data):
        """
        Read next message from stream.
        @param timeout: timeout in seconds
        @param stream_data: protobuf message that is filled with the stream data
        @return functionblock stream meta data (deliveryTimestampUs, sequence)
        @raises TimeoutError: if no data is available within the timeout
        """
        self._logger.debug("Reading stream data with timeout=%s", timeout)
        if not self._stream_queue_sema.acquire(timeout=timeout):
            self._logger.warning("Stream read timeout - no data available")
            raise TimeoutError("No data available within timeout")
        with self._stream_queue_mutex:
            data = self._stream_queue.popleft()
            pb_any_unpack(data.functionSpecificStreamData, stream_data)
            self._logger.debug("Stream data read successfully")
            return data

    @connectable
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

            if response.status == FbPb.Status.TEMPORARILY_UNAVAILABLE:
                raise CommandTemporaryUnavailableError(f"Out of resources: {response.error}")
            elif response.status != FbPb.Status.OK:
                status_str = FbPb.Status.Name(response.status)
                raise RuntimeError(f"Command failed: {status_str}: {response.error}")
            return response

    def _read_thread(self):
        while not self._read_thread_stop:
            msg = FbPb.Response()
            try:
                # Normal timeout - socket closure will interrupt immediately via exception
                self._client.read_msg(msg, 1)  # 1 second is fine since exceptions provide immediate exit
            except TimeoutError:
                # Only exit on timeout if explicitly told to stop
                if self._read_thread_stop:
                    break
                logger.warning("Stream read timeout - no data available")
                continue
            except (ConnectionError, ConnectionAbortedError,
                    ConnectionResetError, RuntimeError) as e:
                # Socket was closed, exit thread immediately
                logger.debug(f"Read thread exiting due to connection drop: {e}")
                break

            if msg.WhichOneof("type") == "stream":
                logger.debug("Received stream message")
                self._feed_stream(msg.stream)
            else:
                logger.debug("Received command response")
                self._cmd_response = msg
                self._cmd_event.set()
        logger.info("Read thread exiting")

    def _feed_stream(self, stream_data):
        with self._stream_queue_mutex:
            self._stream_queue.append(stream_data)
        self._stream_queue_sema.release()
