# SPDX-License-Identifier: Apache-2.0
from typing import Tuple
from io4edge_client.base.connections import ClientConnectionStream, connectable
from io4edge_client.base.logging import io4edge_client_logger
from io4edge_client.functionblock import Client as FbClient
import io4edge_client.api.binaryIoTypeC.python.binaryIoTypeC.v1alpha1.binaryIoTypeC_pb2 as Pb  # noqa: E501


class Client(ClientConnectionStream[Pb.StreamControlStart, Pb.StreamData]):
    """
    binaryIoTypeC functionblock client.
    @param addr: address of io4edge function block (mdns name or "ip:port" address)
    @param command_timeout: timeout for commands in seconds
    """

    def __init__(
        self,
        addr: str,
        command_timeout: int = 5,
        connect: bool = True
    ) -> None:
        self._logger = io4edge_client_logger("binaryiotypec.Client")
        self._logger.debug("Initializing binaryIoTypeC client")
        fb_client = FbClient(
            "_io4edge_binaryIoTypeC._tcp", addr, command_timeout,
            connect=connect
        )
        super().__init__(fb_client)
        # Type hint for better IDE support
        self._client: FbClient = self._client

    def _create_stream_data(self) -> Pb.StreamData:
        """Create binaryIoTypeC-specific StreamData message"""
        return Pb.StreamData()

    def _create_default_stream_config(self) -> Pb.StreamControlStart:
        """Create default binaryIoTypeC-specific StreamControlStart message"""
        return Pb.StreamControlStart()

    @connectable
    def upload_configuration(self, config: Pb.ConfigurationSet) -> None:
        """
        Upload the configuration to the binaryIoTypeC functionblock.
        @param config: configuration to upload
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        """
        self._logger.debug("Uploading configuration to binaryIoTypeC")
        self._client.upload_configuration(config)
        self._logger.info(
            "Configuration uploaded successfully to binaryIoTypeC"
        )

    @connectable
    def download_configuration(self) -> Pb.ConfigurationGetResponse:
        """
        Download the configuration from the binaryIoTypeC functionblock.
        @return: actual configuration
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        """
        fs_response = Pb.ConfigurationGetResponse()
        self._client.download_configuration(Pb.ConfigurationGet(), fs_response)
        return fs_response

    @connectable
    def describe(self) -> Pb.ConfigurationDescribeResponse:
        """
        Get the description from the binaryIoTypeC functionblock.
        @return: description from the binaryIoTypeC functionblock
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        """
        fs_response = Pb.ConfigurationDescribeResponse()
        self._client.describe(Pb.ConfigurationDescribe(), fs_response)
        return fs_response

    @connectable
    def set_output(self, channel: int, state: bool) -> None:
        """
        Set the state of a single output.
        @param channel: channel number
        @param state: state to set. a "true" state sets the output to high, a "false" state sets the output to low
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        """
        self._logger.debug(
            "Setting output channel %s to state %s", channel, state
        )
        fs_cmd = Pb.FunctionControlSet()
        fs_cmd.single.channel = channel
        fs_cmd.single.state = state
        self._client.function_control_set(
            fs_cmd, Pb.FunctionControlSetResponse()
        )
        self._logger.info(
            "Output channel %s set to %s successfully", channel, state
        )

    @connectable
    def set_all_outputs(self, states: int, mask: int) -> None:
        """
        Set the state of all or a group of output channels.
        @param states: binary coded map of outputs. 0 means switch low, 1 means switch high, LSB is Channel0
        @param mask: binary coded map of outputs to be set. 0 means do not change, 1 means change, LSB is Channel0
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        """
        self._logger.debug(
            "Setting all outputs with states=0x%x, mask=0x%x", states, mask
        )
        fs_cmd = Pb.FunctionControlSet()
        fs_cmd.all.states = states
        fs_cmd.all.mask = mask
        self._client.function_control_set(
            fs_cmd, Pb.FunctionControlSetResponse()
        )
        self._logger.info(
            "All outputs set successfully with states=0x%x, mask=0x%x",
            states, mask
        )

    @connectable
    def input(self, channel: int) -> Tuple[bool, int]:
        """
        Get the state of a single channel, regardless whether its configured as input or output)
        and the diagnostic info of a single channel.
        State "true" state means the input is high, a "false" state means the input is low.
        The returned diagnostic info is a bitfield containing diagnostic bits.
        @param channel: channel number
        @return: state of the input, diagnostic info.
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        """
        self._logger.debug("Reading input state for channel %s", channel)
        fs_cmd = Pb.FunctionControlGet()
        fs_cmd.single.channel = channel
        fs_response = Pb.FunctionControlGetResponse()
        self._client.function_control_get(fs_cmd, fs_response)
        state = fs_response.single.state
        self._logger.debug("Input channel %s state: %s", channel, state)
        return state, fs_response.single.diag

    @connectable
    def all_inputs(self) -> Pb.GetAllResponse:
        """
        Get the state of all channels, regardless whether they are configured as input or output.
        Each bit in the returned state corresponds to one channel, bit0 being channel 0.
        The bit is false if the pin level is low, true otherwise.
        diag is a slice with bitfields containing diagnostic bits for each channel.
        """
        fs_cmd = Pb.FunctionControlGet()
        fs_cmd.all.CopyFrom(Pb.GetAll())
        fs_response = Pb.FunctionControlGetResponse()
        self._client.function_control_get(fs_cmd, fs_response)
        return fs_response.all
