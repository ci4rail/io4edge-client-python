# SPDX-License-Identifier: Apache-2.0
from io4edge_client.base.connections import ClientConnection, connectable
from io4edge_client.functionblock import Client as FbClient
import io4edge_client.api.programmablePsu.python.programmablePsu.v1.programmablePsu_pb2 as Pb


class Client(ClientConnection):
    """
    programmablePsu functionblock client.
    @param addr: address of io4edge function block (mdns name or "ip:port" address)
    @param command_timeout: timeout for commands in seconds
    """

    def __init__(self, addr: str, command_timeout=5, connect=True):
        super().__init__(FbClient(
            "_io4edge_colorLED._tcp", addr, command_timeout, connect=connect
        ))

    @connectable
    def describe(self) -> Pb.ConfigurationDescribeResponse:
        """
        Get the description from the colorLED functionblock.
        @return: description from the colorLED functionblock
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        """
        fs_response = Pb.ConfigurationDescribeResponse()
        self._client.describe(Pb.ConfigurationDescribe(), fs_response)
        return fs_response

    @connectable
    def set_voltage_level(self, level: float):
        """
        Set the voltage level of the programmable PSU.
        @param level: voltage level to set (in Volts)
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        """
        fs_cmd = Pb.FunctionControlSet()
        fs_cmd.setVoltageLevel.level = level
        self._client.function_control_set(fs_cmd, Pb.FunctionControlSetResponse())

    @connectable
    def set_output_enabled(self, enabled: bool):
        """
        Set the output enabled state of the programmable PSU.
        @param enabled: if true the output is enabled
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        """
        fs_cmd = Pb.FunctionControlSet()
        fs_cmd.setOutputEnabled.enabled = enabled
        self._client.function_control_set(fs_cmd, Pb.FunctionControlSetResponse())

    @connectable
    def set_current_limit(self, limit: float):
        """
        Set the current limit of the programmable PSU.
        @param limit: current limit to set (in Amperes)
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        """
        fs_cmd = Pb.FunctionControlSet()
        fs_cmd.setCurrentLimit.limit = limit
        self._client.function_control_set(fs_cmd, Pb.FunctionControlSetResponse())


    @connectable
    def get_state(self) -> Pb.FunctionControlGetResponse:
        """
        Get the state of the programmable PSU.
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        """
        fs_cmd = Pb.FunctionControlGet()
        fs_response = Pb.FunctionControlGetResponse()
        self._client.function_control_get(fs_cmd, fs_response)
        return fs_response
