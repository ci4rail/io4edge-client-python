# SPDX-License-Identifier: Apache-2.0
from io4edge_client.base.connections import ClientConnectionStream, connectable
from io4edge_client.base.logging import io4edge_client_logger
from io4edge_client.functionblock import Client as FbClient
import io4edge_client.api.binaryIoTypeB.python.binaryIoTypeB.v1alpha1.binaryIoTypeB_pb2 as Pb  # noqa: E501


class Client(
    ClientConnectionStream[FbClient, Pb.StreamControlStart, Pb.StreamData]
):
    """
    binaryIoTypeB functionblock client.
    @param addr: address of io4edge function block (mdns name or "ip:port" address)
    @param command_timeout: timeout for commands in seconds
    """

    def __init__(
        self,
        addr: str,
        command_timeout: int = 5,
        connect: bool = True
    ) -> None:
        self._logger = io4edge_client_logger("binaryiotypeb.Client")
        self._logger.debug("Initializing binaryIoTypeB client")
        fb_client = FbClient(
            "_io4edge_binaryIoTypeB._tcp", addr, command_timeout,
            connect=connect
        )
        super().__init__(fb_client)
        # Type hint for better IDE support
        self._client: FbClient = self._client

    def _create_stream_data(self) -> Pb.StreamData:
        """Create binaryIoTypeB-specific StreamData message"""
        return Pb.StreamData()

    def _create_default_stream_config(self) -> Pb.StreamControlStart:
        """Create default binaryIoTypeB-specific StreamControlStart message"""
        return Pb.StreamControlStart()

    @connectable
    def describe(self) -> Pb.ConfigurationDescribeResponse:
        """
        Get the description from the binaryIoTypeB functionblock.
        @return: description from the binaryIoTypeB functionblock
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        """
        self._logger.debug("Getting description from binaryIoTypeB")
        fs_response = Pb.ConfigurationDescribeResponse()
        self._client.describe(Pb.ConfigurationDescribe(), fs_response)
        self._logger.info(
            "Description retrieved successfully from binaryIoTypeB"
        )
        return fs_response

    @connectable
    def set_output(self, channel: int, state: bool) -> None:
        """
        Set the state of a single output.
        @param channel: channel number
        @param state: state to set. a "true" state turns on the outputs switch, a "false" state turns it off.
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
        @param states: binary coded map of outputs. 0 means switch off, 1 means switch on, LSB is Channel0
        @param mask: binary coded map of outputs to be set. 0 means do not change, 1 means change, LSB is Channel0
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        """
        self._logger.debug(
            "Setting all outputs with states=0x%x, mask=0x%x", states, mask
        )
        fs_cmd = Pb.FunctionControlSet()
        fs_cmd.all.values = states
        fs_cmd.all.mask = mask
        self._client.function_control_set(
            fs_cmd, Pb.FunctionControlSetResponse()
        )
        self._logger.info(
            "All outputs set successfully with states=0x%x, mask=0x%x",
            states, mask
        )

    @connectable
    def get_input(self, channel: int) -> bool:
        """
        Get the state of a single input.
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
    def get_all_inputs(self) -> int:
        """
        Get the state of all inputs.
        @return: binary coded map of inputs. 0 means switch off, 1 means switch on, LSB is Channel0
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        """
        self._logger.debug("Reading all input states")
        fs_cmd = Pb.FunctionControlGet()
        fs_response = Pb.FunctionControlGetResponse()
        self._client.function_control_get(fs_cmd, fs_response)
        inputs = fs_response.all.values
        self._logger.debug("All inputs state: 0x%x", inputs)
        return inputs
