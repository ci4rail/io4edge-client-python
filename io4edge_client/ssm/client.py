# SPDX-License-Identifier: Apache-2.0
from io4edge_client.base.connections import ClientConnection, connectable
from io4edge_client.base.logging import io4edge_client_logger
from io4edge_client.functionblock import Client as FbClient
from io4edge_client.util.exceptions import InvalidStateError, UnknownError
import io4edge_client.api.ssm.python.ssm.v1.ssm_pb2 as Pb


class Client(ClientConnection):
    """
    System State Manager functionblock client.
    @param addr: address of io4edge function block (mdns name or "ip:port" address)
    @param command_timeout: timeout for commands in seconds
    """

    def __init__(self, addr: str, command_timeout=5, connect=False):
        self._logger = io4edge_client_logger("watchdog.Client")
        self._logger.debug("Initializing watchdog client")
        super().__init__(FbClient("_io4edge_watchdog._tcp", addr, command_timeout, connect=connect))

    @connectable
    def describe(self) -> Pb.ConfigurationDescribeResponse:
        """
        Get the description from the System State Manager functionblock.
        @return: description from the System State Manager functionblock
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        @raises ConnectionError: if not connected to the device
        """
        fs_response = Pb.ConfigurationDescribeResponse()
        self._client.describe(Pb.ConfigurationDescribe(), fs_response)
        return fs_response

    @connectable
    def kick(self):
        """
        Kick the System State Manager to prevent a timeout.
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        @raises ConnectionError: if not connected to the device
        """
        fs_cmd = Pb.FunctionControlSet()
        fs_cmd.kick = True
        fs_response = Pb.FunctionControlSetResponse()
        self._client.function_control_set(fs_cmd, fs_response)

    @property
    @connectable
    def state(self) -> Pb.SystemState:
        """
        Get the current state from the System State Manager functionblock.
        @return: current state from the System State Manager functionblock
        @raises RuntimeError: if the command fails or unhandled response
        @raises TimeoutError: if the command times out
        @raises ConnectionError: if not connected to the device
        """
        fs_response = Pb.FunctionControlGetResponse()
        self._client.function_control_get(Pb.FunctionControlGet(), fs_response)

        if fs_response.state is not None:
            return fs_response.state
        else:
            raise RuntimeError("Failed to retrieve state from SSM functionblock")

    @connectable
    def error(self, msg: str) -> None:
        """
        Set error state with given log message.

        @param msg: error message
        @raises RuntimeError: if command fails or unhandled response
        @raises TimeoutError: if the command times out
        @raises ConnectionError: if not connected to the device
        @raises InvalidStateError: if operation attempted in an invalid state
        @raises UnknownError: if unknown error occurs while setting error state
        """
        fs_cmd = Pb.FunctionControlSet()
        fs_cmd.error = msg
        fs_response = Pb.FunctionControlSetResponse()
        self._client.function_control_set(fs_cmd, fs_response)

        # exception handling based on response
        match fs_response.response:
            case Pb.StateCommandResponse.STATE_OK:
                return
            case Pb.StateCommandResponse.INVALID_STATE_ERROR:
                msg = fs_response.message
                raise InvalidStateError(
                    "Invalid state for setting error: ", msg)
            case Pb.StateCommandResponse.UNKNOWN_STATE_ERROR:
                msg = fs_response.message
                raise UnknownError("Unknown error while setting error: " + msg)
            case _:
                raise RuntimeError("Unhandled response from SSM functionblock")

    @connectable
    def resolve(self, msg: str) -> None:
        """
        Resolve current error state.
        @param msg: resolution message
        @raises RuntimeError: if command fails or unhandled response
        @raises TimeoutError: if the command times out
        @raises ConnectionError: if not connected to the device
        @raises InvalidStateError: if operation attempted in an invalid state
        @raises UnknownError: if unknown error occurs while resolving error
        """
        fs_cmd = Pb.FunctionControlSet()
        fs_cmd.resolve = msg
        fs_response = Pb.FunctionControlSetResponse()
        self._client.function_control_set(fs_cmd, fs_response)

        # exception handling based on response
        match fs_response.response:
            case Pb.StateCommandResponse.STATE_OK:
                return
            case Pb.StateCommandResponse.INVALID_STATE_ERROR:
                msg = fs_response.message
                raise InvalidStateError(
                    "Invalid state for resolving error: ", msg)
            case Pb.StateCommandResponse.UNKNOWN_STATE_ERROR:
                msg = fs_response.message
                raise UnknownError(
                    "Unknown error while resolving error: " + msg)
            case _:
                raise RuntimeError("Unhandled response from SSM functionblock")

    @connectable
    def fatal(self, msg: str) -> None:
        """
        Signal a fatal error.

        @param msg: fatal error message
        @raises RuntimeError: if command fails or unhandled response
        @raises TimeoutError: if the command times out
        @raises ConnectionError: if not connected to the device
        @raises InvalidStateError: if operation attempted in an invalid state
        @raises UnknownError: if unknown error occurs signaling fatal error
        """
        fs_cmd = Pb.FunctionControlSet()
        fs_cmd.fatal = msg
        fs_response = Pb.FunctionControlSetResponse()
        self._client.function_control_set(fs_cmd, fs_response)

        # exception handling based on response
        match fs_response.response:
            case Pb.StateCommandResponse.STATE_OK:
                return
            case Pb.StateCommandResponse.INVALID_STATE_ERROR:
                msg = fs_response.message
                raise InvalidStateError("Invalid state for fatal error: ", msg)
            case Pb.StateCommandResponse.UNKNOWN_STATE_ERROR:
                msg = fs_response.message
                raise UnknownError(
                    "Unknown error while signaling fatal error: " + msg)
            case _:
                raise RuntimeError("Unhandled response from SSM functionblock")

    @connectable
    def shutdown(self) -> None:
        """
        Indicate system shutdown.
        @raises RuntimeError: if command fails or unhandled response
        @raises TimeoutError: if the command times out
        @raises ConnectionError: if not connected to the device
        @raises InvalidStateError: if operation attempted in an invalid state
        @raises UnknownError: if unknown error occurs while signaling shutdown
        """
        fs_cmd = Pb.FunctionControlSet()
        fs_cmd.shutdown = True
        fs_response = Pb.FunctionControlSetResponse()
        self._client.function_control_set(fs_cmd, fs_response)

        # exception handling based on response
        match fs_response.response:
            case Pb.StateCommandResponse.CMD_OK:
                return
            case Pb.StateCommandResponse.INVALID_CMD_STATE_ERROR:
                msg = fs_response.message
                raise InvalidStateError(
                    "Invalid state for shutdown signal: ", msg)
            case Pb.StateCommandResponse.UNKNOWN_CMD_ERROR:
                msg = fs_response.message
                raise UnknownError(
                    "Unknown error while signaling shutdown: " + msg)
            case _:
                raise RuntimeError("Unhandled response from SSM functionblock")

    @connectable
    def on(self) -> None:
        """
        Signals ON state.

        @raises RuntimeError: if command fails or unhandled response
        @raises TimeoutError: if the command times out
        @raises ConnectionError: if not connected to the device
        @raises InvalidStateError: if operation attempted in an invalid state
        @raises UnknownError: if unknown error occurs while turning on
        """
        fs_cmd = Pb.FunctionControlSet()
        fs_cmd.on = True
        fs_response = Pb.FunctionControlSetResponse()
        self._client.function_control_set(fs_cmd, fs_response)

        # exception handling based on response
        match fs_response.response:
            case Pb.HostCommandResponse.CMD_OK:
                return
            case Pb.HostCommandResponse.INVALID_CMD_STATE_ERROR:
                msg = fs_response.message
                raise InvalidStateError("Invalid state for turning on: ", msg)
            case Pb.HostCommandResponse.UNKNOWN_CMD_ERROR:
                msg = fs_response.message
                raise UnknownError("Unknown error while turning on: " + msg)
            case _:
                raise RuntimeError("Unhandled response from SSM functionblock")

    @connectable
    def reboot(self) -> None:
        """
        Signals a reboot.

        @raises RuntimeError: if command fails or unhandled response
        @raises TimeoutError: if the command times out
        @raises ConnectionError: if not connected to the device
        @raises InvalidStateError: if operation attempted in an invalid state
        @raises UnknownError: if unknown error occurs while signaling reboot
        """
        fs_cmd = Pb.FunctionControlSet()
        fs_cmd.reboot = True
        fs_response = Pb.FunctionControlSetResponse()
        self._client.function_control_set(fs_cmd, fs_response)

        # exception handling based on response
        match fs_response.response:
            case Pb.HostCommandResponse.CMD_OK:
                return
            case Pb.HostCommandResponse.INVALID_CMD_STATE_ERROR:
                msg = fs_response.message
                raise InvalidStateError(
                    "Invalid state for signaling reboot: ", msg)
            case Pb.HostCommandResponse.UNKNOWN_CMD_ERROR:
                msg = fs_response.message
                raise UnknownError(
                    "Unknown error while signaling reboot: " + msg)
            case _:
                raise RuntimeError("Unhandled response from SSM functionblock")
