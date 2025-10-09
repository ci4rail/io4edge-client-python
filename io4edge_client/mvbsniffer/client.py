# SPDX-License-Identifier: Apache-2.0
from io4edge_client.base.connections import ClientConnectionStream, connectable
from io4edge_client.functionblock import Client as FbClient
import io4edge_client.api.mvbSniffer.python.mvbSniffer.v1.mvbSniffer_pb2 as Pb
import io4edge_client.api.mvbSniffer.python.mvbSniffer.v1.telegram_pb2 as TelegramPb
import io4edge_client.api.io4edge.python.functionblock.v1alpha1.io4edge_functionblock_pb2 as FbPb


class Client(ClientConnectionStream[Pb.StreamControlStart, Pb.StreamData]):
    """
    mvbSniffer functionblock client.
    @param addr: address of io4edge function block (mdns name or "ip:port" address)
    @param command_timeout: timeout for commands in seconds
    """

    def __init__(self, addr: str, command_timeout=5, connect=True):
        super().__init__(FbClient("_io4edge_mvbSniffer._tcp", addr, command_timeout, connect=connect))

    def _create_stream_data(self) -> Pb.StreamData:
        """Create mvbSniffer-specific StreamData message"""
        return Pb.StreamData()

    def _create_default_stream_config(self) -> Pb.StreamControlStart:
        """Create default mvbSniffer-specific StreamControlStart message"""
        return Pb.StreamControlStart()

    @connectable
    def send_pattern(self, msg: str):
        """
        Send a pattern to the mvbSniffer's internal mvb frame generator.
        See https://github.com/ci4rail/io4edge-client-go/blob/main/mvbsniffer/generator.go how to create the pattern.
        @param msg: pattern to send
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        """
        fs_cmd = Pb.FunctionControlSet(generator_pattern=msg)
        self._client.function_control_set(fs_cmd, Pb.FunctionControlSetResponse())

    def read_stream_telegrams(self, timeout=None):
        """
        Read the next message from the stream as TelegramCollection.
        @param timeout: timeout in seconds
        @return: functionblock generic stream data (deliveryTimestampUs, sequence), mvbSniffer TelegramCollection
        @raises TimeoutError: if no data is available within the timeout
        """
        stream_data = TelegramPb.TelegramCollection()
        generic_stream_data = self._client.read_stream(timeout, stream_data)
        return generic_stream_data, stream_data
