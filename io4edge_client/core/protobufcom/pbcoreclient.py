from io4edge_client.base import Client as BaseClient
import io4edge_client.api.io4edge.python.core_api.v1alpha2.io4edge_core_api_pb2 as Pb
from typing import Tuple

class PbCoreClient:
    """
    io4edge core client using protobuf communication.
    @param addr: address of io4edge function block (mdns name or "ip:port" address)
    @param command_timeout: timeout for commands in seconds
    """

    def __init__(self, addr: str, command_timeout=5):
        self._client = BaseClient("_io4edge-core._tcp", addr)
        self._command_timeout = command_timeout

    def command(self, cmd, response):
        """
        Send a command to the io4edge core.
        @param cmd: protobuf message with the command
        @param response: protobuf message that is filled with the response
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        """
        self._client.write_msg(cmd)
        self._client.read_msg(response, self._command_timeout)
        if response.id != cmd.id:
            raise RuntimeError("Unexpected response ID")

    def identify_firmware(self) -> Tuple[str,str]:
        """
        Identify the firmware version of the io4edge core.
        @return: firmware version as a string
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        """
        cmd = Pb.CoreCommand(id=Pb.CommandId.IDENTIFY_FIRMWARE)
        response = Pb.CoreResponse()
        self.command(cmd, response)
        return response.identify_firmware.name, response.identify_firmware.version
