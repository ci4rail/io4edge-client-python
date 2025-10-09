# SPDX-License-Identifier: Apache-2.0
from io4edge_client.base.connections import ClientConnectionStream, connectable
from io4edge_client.functionblock import Client as FbClient
import io4edge_client.api.analogInTypeA.python.analogInTypeA.v1alpha1.analogInTypeA_pb2 as Pb
import io4edge_client.api.io4edge.python.functionblock.v1alpha1.io4edge_functionblock_pb2 as FbPb


class Client(ClientConnectionStream[Pb.StreamControlStart, Pb.StreamData]):
    """
    analogInTypeA functionblock client.
    @param addr: address of io4edge function block (mdns name or "ip:port" address)
    @param command_timeout: timeout for commands in seconds
    """

    def __init__(self, addr: str, command_timeout=5, connect=True):
        super().__init__(FbClient("_io4edge_analogInTypeA._tcp", addr, command_timeout, connect=connect))

    def _create_stream_data(self) -> Pb.StreamData:
        """Create analogInTypeA-specific StreamData message"""
        return Pb.StreamData()

    def _create_default_stream_config(self) -> Pb.StreamControlStart:
        """Create default analogInTypeA-specific StreamControlStart message"""
        return Pb.StreamControlStart()

    @connectable
    def upload_configuration(self, config: Pb.ConfigurationSet):
        """
        Upload the configuration to the analogInTypeA functionblock.
        @param config: configuration to upload
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        """
        self._client.upload_configuration(config)

    @connectable
    def download_configuration(self) -> Pb.ConfigurationGetResponse:
        """
        Download the configuration from the analogInTypeA functionblock.
        @return: actual configuration
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        """
        fs_response = Pb.ConfigurationGetResponse()
        self._client.download_configuration(Pb.ConfigurationGet(), fs_response)
        return fs_response

    @connectable
    def value(self) -> float:
        """
        read the current analog input level.

        @return: current analog input level. range -1 .. +1 (for min/max voltage or current)
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        """
        fs_cmd = Pb.FunctionControlGet()
        fs_response = Pb.FunctionControlGetResponse()
        self._client.function_control_get(fs_cmd, fs_response)
        return fs_response.value
