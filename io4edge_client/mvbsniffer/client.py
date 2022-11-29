# SPDX-License-Identifer: Apache-2.0
from io4edge_client.functionblock import Client as FbClient
import io4edge_client.api.mvbSniffer.python.mvbSniffer.v1.mvbSniffer_pb2 as Pb
import io4edge_client.api.mvbSniffer.python.mvbSniffer.v1.telegram_pb2 as TelegramPb
import io4edge_client.api.io4edge.python.functionblock.v1alpha1.io4edge_functionblock_pb2 as FbPb


class Client:
    """
    mvbSniffer functionblock client.
    @param addr: address of io4edge function block (mdns name or "ip:port" address)
    @param command_timeout: timeout for commands in seconds
    """

    def __init__(self, addr: str, command_timeout=5):
        self._fb_client = FbClient("_io4edge_mvbSniffer._tcp", addr, command_timeout)

    def send_pattern(self, msg: str):
        """
        Send a pattern to the mvbSniffer's internal mvb frame generator.
        See https://github.com/ci4rail/io4edge-client-go/blob/main/mvbsniffer/generator.go how to create the pattern.
        @param msg: pattern to send
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        """
        fs_cmd = Pb.FunctionControlSet(generator_pattern=msg)
        self._fb_client.function_control_set(fs_cmd, Pb.FunctionControlSetResponse())

    def start_stream(
        self, config: Pb.StreamControlStart, fb_config: FbPb.StreamControl
    ):
        """
        Start streaming of mvbSniffer data.
        @param config: mvb specific filter configuration of the stream
        @param fb_config: functionblock generic configuration of the stream
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        """
        self._fb_client.start_stream(config, fb_config)

    def stop_stream(self):
        """
        Stop streaming of mvbSniffer data.
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        """
        self._fb_client.stop_stream()

    def read_stream(self, timeout=None):
        """
        Read the next message from the stream.
        @param timeout: timeout in seconds
        @return: functionblock generic stream data (deliveryTimestampUs, sequence), mvbSniffer TelegramCollection
        @raises TimeoutError: if no data is available within the timeout
        """
        stream_data = TelegramPb.TelegramCollection()
        generic_stream_data = self._fb_client.read_stream(timeout, stream_data)
        return generic_stream_data, stream_data

    def close(self):
        """
        Close the connection to the function block, terminate read thread.
        After calling this method, the object is no longer usable.
        """
        self._fb_client.close()
