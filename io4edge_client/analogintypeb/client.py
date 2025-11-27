# SPDX-License-Identifier: Apache-2.0
from io4edge_client.base.connections import ClientConnectionStream, connectable
from io4edge_client.base.logging import io4edge_client_logger
from io4edge_client.functionblock import Client as FbClient
import io4edge_client.api.analogInTypeB.python.analogInTypeB.v1.analogInTypeB_pb2 as Pb
import io4edge_client.api.io4edge.python.functionblock.v1alpha1.io4edge_functionblock_pb2 as FbPb


class Client(ClientConnectionStream[Pb.StreamControlStart, Pb.StreamData]):
    """
    analogInTypeB functionblock client.
    @param addr: address of io4edge function block (mdns name or "ip:port" address)
    @param command_timeout: timeout for commands in seconds
    """

    def __init__(self, addr: str, command_timeout=5, connect=True):
        self._logger = io4edge_client_logger("analogintypeb.Client")
        self._logger.debug("Initializing analogInTypeB client for addr='%s', "
                           "timeout=%s", addr, command_timeout)
        super().__init__(FbClient("_io4edge_analogInTypeB._tcp", addr, command_timeout, connect=connect))

    def _create_stream_data(self) -> Pb.StreamData:
        """Create analogInTypeB-specific StreamData message"""
        return Pb.StreamData()

    def _create_default_stream_config(self) -> Pb.StreamControlStart:
        """Create default analogInTypeB-specific StreamControlStart message"""
        return Pb.StreamControlStart()

    def start_stream(self, channel_mask: int, fb_config: FbPb.StreamControl):
        """
        Start streaming of analogInTypeB data.
        @param channel_mask: channels to enable for the stream
        @param fb_config: functionblock generic configuration of the stream
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        """
        self._logger.debug("Starting stream for analogInTypeB with "
                           "channel_mask=%s", channel_mask)
        config = Pb.StreamControlStart(channelMask=channel_mask)
        super().start_stream(config, fb_config)
        self._logger.info("Stream started successfully for analogInTypeB")

    @connectable
    def upload_configuration(self, config: Pb.ConfigurationSet):
        """
        Upload the configuration to the analogInTypeB functionblock.
        @param config: configuration to upload
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        """
        self._logger.debug("Uploading configuration to analogInTypeB")
        self._client.upload_configuration(config)
        self._logger.info("Configuration uploaded successfully to "
                          "analogInTypeB")

    @connectable
    def download_configuration(self) -> Pb.ConfigurationGetResponse:
        """
        Download the configuration from the analogInTypeB functionblock.
        @return: actual configuration
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        """
        self._logger.debug("Downloading configuration from analogInTypeB")
        fs_response = Pb.ConfigurationGetResponse()
        self._client.download_configuration(Pb.ConfigurationGet(), fs_response)
        self._logger.info("Configuration downloaded successfully from "
                          "analogInTypeB")
        return fs_response

    @connectable
    def describe(self) -> Pb.ConfigurationDescribeResponse:
        """
        Get the description from the analogInTypeB functionblock.
        @return: description from the analogInTypeB functionblock
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        """
        fs_response = Pb.ConfigurationDescribeResponse()
        self._client.describe(Pb.ConfigurationDescribe(), fs_response)
        return fs_response

    @connectable
    def value(self) -> list[float]:
        """
        read the current analog input level of all channels.

        @return: a list of values with the current analog input level. range -1 .. +1 (for min/max voltage or current)
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        """
        fs_cmd = Pb.FunctionControlGet()
        fs_response = Pb.FunctionControlGetResponse()
        self._client.function_control_get(fs_cmd, fs_response)
        return fs_response.value
