# SPDX-License-Identifier: Apache-2.0
from io4edge_client.base.connections import ClientConnection, connectable
from io4edge_client.base.logging import io4edge_client_logger
from io4edge_client.functionblock import Client as FbClient
import io4edge_client.api.binaryIoTypeD.python.binaryIoTypeD.v1.binaryIoTypeD_pb2 as Pb


class Client(ClientConnection):
    """
    binaryIoTypeD functionblock client.
    @param addr: address of io4edge function block (mdns name or "ip:port" address)
    @param command_timeout: timeout for commands in seconds
    """

    def __init__(self, addr: str, command_timeout=5, connect=True):
        self._logger = io4edge_client_logger("binaryiotyped.Client")
        self._logger.debug("Initializing binaryiotyped client")
        super().__init__(FbClient("_io4edge_binaryIoTypeD._tcp", addr, command_timeout, connect=connect))

    @connectable
    def upload_configuration(self, config: Pb.ConfigurationSet):
        """
        Upload the configuration to the binaryIoTypeD functionblock.
        @param config: configuration to upload
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        """
        self._logger.debug("Uploading configuration to binaryiotyped")
        self._client.upload_configuration(config)
        self._logger.info("Configuration uploaded successfully to binaryiotyped")

    @connectable
    def download_configuration(self) -> Pb.ConfigurationGetResponse:
        """
        Download the configuration from the binaryIoTypeD functionblock.
        @return: actual configuration
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        """
        fs_response = Pb.ConfigurationGetResponse()
        self._client.download_configuration(Pb.ConfigurationGet(), fs_response)
        return fs_response

    @connectable
    def set_output(self, channel: int, state: bool):
        self._logger.debug("Setting output channel %s to state %s", channel, state)
        """
        Set the state of a single output.
        @param channel: channel number
        @param state: state to set. a "true" state turns on the output switch, a "false" state turns it off.
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        """
        fs_cmd = Pb.FunctionControlSet()
        fs_cmd.single.channel = channel
        fs_cmd.single.state = state
        self._client.function_control_set(fs_cmd, Pb.FunctionControlSetResponse())
        self._logger.info("Output channel %s set to %s successfully", channel, state)

    @connectable
    def set_outputs(self, states: int, mask: int):
        """
        Set the state of all or a group of output channels.
        @param states: binary coded map of outputs. 0 means switch off, 1 means switch on, LSB is Channel0
        @param mask: binary coded map of outputs to be set. 0 means do not change, 1 means change, LSB is Channel0
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        """
        fs_cmd = Pb.FunctionControlSet()
        fs_cmd.all.values = states
        fs_cmd.all.mask = mask
        self._client.function_control_set(fs_cmd, Pb.FunctionControlSetResponse())

    @connectable
    def get_channels(self) -> Pb.FunctionControlGetResponse:
        """
        Get the state of all channels, regardless whether they are configured as input or output.
        Each bit in the returned "inputs" corresponds to one channel, bit0 being channel 0.
        The bit is false if the pin level is inactive, or true if active.
        diag is a slice with bitfields containing diagnostic bits for each channel.
        @return: state of all inputs plus diagnostic info
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        """
        fs_cmd = Pb.FunctionControlGet()
        fs_response = Pb.FunctionControlGetResponse()
        self._client.function_control_get(fs_cmd, fs_response)
        return fs_response
