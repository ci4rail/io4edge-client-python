# SPDX-License-Identifier: Apache-2.0
from io4edge_client.functionblock import Client as FbClient
import io4edge_client.api.watchdog.python.watchdog.v1.watchdog_pb2 as Pb


class Client:
    """
     functionblock client.
    @param addr: address of io4edge function block (mdns name or "ip:port" address)
    @param command_timeout: timeout for commands in seconds
    """

    def __init__(self, addr: str, command_timeout=5, connect=True):
        self._fb_client = FbClient("_io4edge_watchdog._tcp", addr, command_timeout, connect=connect)

    def describe(self) -> Pb.ConfigurationDescribeResponse:
        """
        Get the description from the watchdog functionblock.
        @return: description from the watchdog functionblock
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        """
        fs_response = Pb.ConfigurationDescribeResponse()
        self._fb_client.describe(Pb.ConfigurationDescribe(), fs_response)
        return fs_response

    def kick(self):
        """
        Kick the watchdog to prevent a timeout.
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        """
        fs_cmd = Pb.FunctionControlSet()
        fs_cmd.kick = True
        self._fb_client.function_control_set(fs_cmd, Pb.FunctionControlSetResponse())

    def close(self):
        """
        Close the connection to the function block, terminate read thread.
        After calling this method, the object is no longer usable.
        """
        self._fb_client.close()
