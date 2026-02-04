# SPDX-License-Identifier: Apache-2.0
from typing import Optional
from io4edge_client.base.connections import ClientConnection, connectable
from io4edge_client.base.logging import io4edge_client_logger
from io4edge_client.functionblock import Client as FbClient
from io4edge_client.util.exceptions import UnknownError
import io4edge_client.api.eeprom.python.eeprom.v1alpha1.eeprom_pb2 as Pb


class Client(ClientConnection):
    """
    EEPROM functionblock client.

    @param addr: address of io4edge function block (mdns name or "ip:port" address)
    @param command_timeout: timeout for commands in seconds
    """

    def __init__(
        self,
        addr: str,
        command_timeout: int = 5,
        connect: bool = False
    ) -> None:
        self._logger = io4edge_client_logger("eeprom.Client")
        self._logger.debug("Initializing EEPROM client")
        fb_client = FbClient(
            "_io4edge_eeprom._tcp", addr, command_timeout,
            connect=connect
        )
        super().__init__(fb_client)
        # Type hint for better IDE support
        self._client: FbClient = self._client

        self.size: int = self.describe().size

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
    def read(self, length: Optional[int] = None, start: int = 0) -> Pb.EepromReadResponse:
        """
        Read from the EEPROM.

        @return: data read from EEPROM
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        @raises ConnectionError: if not connected to the device
        """

        length = self.size if length is None else length

        if length <= 0:
            raise ValueError("Length to read must be positive")
        elif start < 0 or start >= self.size:
            raise ValueError("Start address out of bounds")
        elif start + length > self.size:
            raise ValueError("Read exceeds EEPROM size from start address")

        fs_cmd = Pb.FunctionControlGet()
        fs_cmd.read = Pb.EepromReadRequest()
        fs_cmd.read.address = start
        fs_cmd.read.length = length

        fs_response = Pb.FunctionControlGetResponse()
        self._client.function_control_get(fs_cmd, fs_response)

        if fs_response.read_response is not None:
            return fs_response.read_response
        else:
            raise RuntimeError("Failed to retrieve data from EEPROM functionblock")

    @connectable
    def write(self, data: bytes, start: int = 0) -> None:
        """
        Write to the EEPROM.

        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        @raises ConnectionError: if not connected to the device
        """
        if len(data) == 0:
            raise ValueError("Data to write cannot be empty")
        elif start < 0 or start >= self.size:
            raise ValueError("Start address out of bounds")
        elif start + len(data) > self.size:
            raise ValueError("Data exceeds EEPROM size from start address")

        fs_cmd = Pb.FunctionControlSet()
        fs_cmd.write = Pb.EepromWriteRequest()
        fs_cmd.write.address = start
        fs_cmd.write.data = data

        fs_response = Pb.FunctionControlSetResponse()
        self._client.function_control_set(fs_cmd, fs_response)

    @connectable
    def status(self) -> Pb.EepromStatusResponse:
        """
        Get the current state from the System State Manager functionblock.

        @return: current state from the System State Manager functionblock
        @raises RuntimeError: if the command fails or unhandled response
        @raises TimeoutError: if the command times out
        @raises ConnectionError: if not connected to the device
        """
        fs_response = Pb.FunctionControlGetResponse()
        self._client.function_control_get(Pb.FunctionControlGet(), fs_response)

        if fs_response.status_response is not None:
            return fs_response.status_response
        else:
            raise RuntimeError("Failed to retrieve status from EEPROM functionblock")
