# SPDX-License-Identifier: Apache-2.0
from io4edge_client.base.connections import ClientConnectionStream, connectable
from io4edge_client.base.logging import io4edge_client_logger
from io4edge_client.functionblock import Client as FbClient
import io4edge_client.api.binaryIoTypeA.python.binaryIoTypeA.v1alpha1.binaryIoTypeA_pb2 as Pb  # noqa: E501


class Client(ClientConnectionStream[Pb.StreamControlStart, Pb.StreamData]):
    """
    binaryIoTypeA functionblock client.
    @param addr: address of io4edge function block (mdns name or "ip:port" address)
    @param command_timeout: timeout for commands in seconds
    """

    def __init__(
        self,
        addr: str,
        command_timeout: int = 5,
        connect: bool = True
    ) -> None:
        self._logger = io4edge_client_logger("binaryiotypea.Client")
        self._logger.debug("Initializing binaryIoTypeA client")
        super().__init__(
            FbClient(
                "_io4edge_binaryIoTypeA._tcp", addr, command_timeout,
                connect=connect
            )
        )

    def _create_stream_data(self) -> Pb.StreamData:
        """Create binaryIoTypeA-specific StreamData message"""
        return Pb.StreamData()

    def _create_default_stream_config(self) -> Pb.StreamControlStart:
        """Create default binaryIoTypeA-specific StreamControlStart message"""
        return Pb.StreamControlStart()

    @connectable
    def upload_configuration(self, config: Pb.ConfigurationSet) -> None:
        """
        Upload the configuration to the binaryIoTypeA functionblock.
        @param config: configuration to upload
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        """
        self._logger.debug("Uploading configuration to binaryiotypea")
        self._client.upload_configuration(config)
        self._logger.info(
            "Configuration uploaded successfully to binaryiotypea"
        )

    @connectable
    def download_configuration(self) -> Pb.ConfigurationGetResponse:
        """
        Download the configuration from the binaryIoTypeA functionblock.
        @return: actual configuration
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        """
        self._logger.debug("Downloading configuration from binaryiotypea")
        fs_response = Pb.ConfigurationGetResponse()
        self._client.download_configuration(Pb.ConfigurationGet(), fs_response)
        self._logger.info("Configuration downloaded successfully from "
                          "binaryiotypea")
        return fs_response

    @connectable
    def describe(self) -> Pb.ConfigurationDescribeResponse:
        """
        Get the description from the binaryIoTypeA functionblock.
        @return: description from the binaryIoTypeA functionblock
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        """
        self._logger.debug("Getting description from binaryiotypea")
        fs_response = Pb.ConfigurationDescribeResponse()
        self._client.describe(Pb.ConfigurationDescribe(), fs_response)
        self._logger.info("Description retrieved successfully from "
                          "binaryiotypea")
        return fs_response

    @connectable
    def set_output(self, channel: int, state: bool):
        """
        Set the state of a single output.
        @param channel: channel number
        @param state: state to set. a "true" state turns on the outputs switch, a "false" state turns it off.
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        """
        self._logger.debug("Setting output channel %s to state %s",
                           channel, state)
        fs_cmd = Pb.FunctionControlSet()
        fs_cmd.single.channel = channel
        fs_cmd.single.state = state
        self._client.function_control_set(fs_cmd, Pb.FunctionControlSetResponse())
        self._logger.info("Output channel %s set to %s successfully",
                          channel, state)

    @connectable
    def set_all_outputs(self, states: int, mask: int):
        """
        Set the state of all or a group of output channels.
        @param states: binary coded map of outputs. 0 means switch off, 1 means switch on, LSB is Channel0
        @param mask: binary coded map of outputs to be set. 0 means do not change, 1 means change, LSB is Channel0
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        """
        self._logger.debug("Setting all outputs with states=0x%x, mask=0x%x",
                           states, mask)
        fs_cmd = Pb.FunctionControlSet()
        fs_cmd.all.values = states
        fs_cmd.all.mask = mask
        self._client.function_control_set(fs_cmd, Pb.FunctionControlSetResponse())
        self._logger.info("All outputs set successfully with states=0x%x, "
                          "mask=0x%x", states, mask)

    @connectable
    def exit_error_state(self):
        """
        Try to recover the binary output controller from error state.
        The binary output controller enters error state when there is an overurrent condition for a long time.
        In the error state, no outputs can be set; inputs can still be read.
        This call tells the binary output controller to try again.
        This call does however not wait if the recovery was successful or not.
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        """
        self._logger.debug("Attempting to exit error state")
        fs_cmd = Pb.FunctionControlSet()
        fs_cmd.exit_error.CopyFrom(Pb.SetExitError())
        self._client.function_control_set(fs_cmd, Pb.FunctionControlSetResponse())
        self._logger.info("Exit error state command sent successfully")

    @connectable
    def input(self, channel: int) -> bool:
        """
        Get the state of a single channel, regardless whether its configured as input or output)
        State "true" is returned if the input level is above switching threshold, "false" otherwise.
        @param channel: channel number
        @return: state of the input
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
        return state

    @connectable
    def all_inputs(self, mask: int) -> int:
        """
        Get the state of all channels, regardless whether they are configured as input or output.
        Each bit in the returned state corresponds to one channel, bit0 being channel 0.
        The bit is "true" if the input level is above switching threshold, "false" otherwise.

        @param: mask to define which channels are read. 0 means mask, 1 means unmask, LSB is Channel0
        @return: state of all inputs
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        """
        self._logger.debug("Reading all inputs with mask=0x%x", mask)
        fs_cmd = Pb.FunctionControlGet()
        fs_cmd.all.mask = mask
        fs_response = Pb.FunctionControlGetResponse()
        self._client.function_control_get(fs_cmd, fs_response)
        inputs = fs_response.all.inputs
        self._logger.debug("All inputs state: 0x%x", inputs)
        return inputs
