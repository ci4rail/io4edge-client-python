# SPDX-License-Identifier: Apache-2.0
from io4edge_client.base.connections import ClientConnection, connectable
from io4edge_client.base.logging import io4edge_client_logger
from io4edge_client.functionblock import Client as FbClient
import io4edge_client.api.watchdog.python.watchdog.v1.watchdog_pb2 as Pb


class Client(ClientConnection):
    """
     functionblock client.
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
        Get the description from the watchdog functionblock.
        @return: description from the watchdog functionblock
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        """
        fs_response = Pb.ConfigurationDescribeResponse()
        self._client.describe(Pb.ConfigurationDescribe(), fs_response)
        return fs_response

    @connectable
    def kick(self):
        """
        Kick the watchdog to prevent a timeout.
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        """
        fs_cmd = Pb.FunctionControlSet()
        fs_cmd.kick = True
        self._client.function_control_set(fs_cmd, Pb.FunctionControlSetResponse())
