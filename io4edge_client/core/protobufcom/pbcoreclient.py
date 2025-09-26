from contextlib import contextmanager
import os
import sys
from io4edge_client.base import Client as BaseClient
import io4edge_client.api.io4edge.python.core_api.v1alpha2.io4edge_core_api_pb2 as Pb
from ..types import FirmwareIdentification, HardwareIdentification
from typing import Callable, Optional


class PbCoreClient:
    """
    io4edge core client using protobuf communication.
    @param addr: address of io4edge function block (mdns name or "ip:port" address)
    @param command_timeout: timeout for commands in seconds
    """

    def __init__(self, addr: str, command_timeout=5):
        self._addr = addr
        self._command_timeout = command_timeout
        self._client: BaseClient | None = BaseClient("_io4edge-core._tcp", self._addr, connect=False)

    def command(self, cmd, response):
        """
        Send a command to the io4edge core.
        @param cmd: protobuf message with the command
        @param response: protobuf message that is filled with the response
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        """
        with self._client as client:
            client.write_msg(cmd)
            client.read_msg(response, self._command_timeout)
            # Due to a bug in the io4edge core, the response ID is not set correctly in the get/set parameter response.
            if response.id != cmd.id and cmd.id != Pb.CommandId.GET_PERSISTENT_PARAMETER and cmd.id != Pb.CommandId.SET_PERSISTENT_PARAMETER:
                raise RuntimeError(
                    f"Unexpected response ID, expected {cmd.id}, got {response.id}")
            if response.status != Pb.Status.OK:
                raise RuntimeError(
                    f"Command failed with status {response.status} ({Pb.Status.Name(response.status)})")

    def identify_hardware(self) -> HardwareIdentification:
        """
        Identify the hardware of io4edge device.
        @return: hardware identification containing root article, major version, and serial number
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        """
        cmd = Pb.CoreCommand(id=Pb.CommandId.IDENTIFY_HARDWARE)
        response = Pb.CoreResponse()
        self.command(cmd, response)
        return HardwareIdentification(
            response.identify_hardware.root_article,
            response.identify_hardware.major_version,
            response.identify_hardware.serial_number,
        )

    def program_hardware_identification(
        self, root_article: str, major_version: int, serial_number: str
    ) -> None:
        raise NotImplementedError(
            "Programming hardware identification is not implemented yet"
        )

    def identify_firmware(self) -> FirmwareIdentification:
        """
        Identify the firmware version of io4edge device.
        @return: firmware identification containing name and version
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        """
        cmd = Pb.CoreCommand(id=Pb.CommandId.IDENTIFY_FIRMWARE)
        response = Pb.CoreResponse()
        self.command(cmd, response)
        return FirmwareIdentification(
            response.identify_firmware.name,
            response.identify_firmware.version
        )

    def load_firmware(self, firmware: bytes, progress_cb: Optional[Callable[[float], None]]) -> None:
        """
        Load firmware to io4edge device.
        `firmware` must be the raw binary file, not a .fwpkg file.
        @param firmware: firmware binary data
        @param progress_cb: callback function that is called with progress updates (0-100)
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        """
        chunk_number = 0
        total_size = len(firmware)
        transferred_size = 0

        while True:
            chunk_size = min(len(firmware), 1024)
            chunk = firmware[:chunk_size]
            firmware = firmware[chunk_size:]
            chunk_cmd = Pb.LoadFirmwareChunkCommand(
                chunk_number=chunk_number,
                is_last_chunk=len(firmware) == 0,
                data=chunk,
            )
            cmd = Pb.CoreCommand(
                id=Pb.CommandId.LOAD_FIRMWARE_CHUNK,
                load_firmware_chunk=chunk_cmd)
            self.command(cmd, Pb.CoreResponse())
            transferred_size += chunk_size
            if progress_cb:
                # Update progress callback with percentage
                progress_cb(
                    transferred_size / total_size * 100 if total_size > 0 else 100)
            if len(firmware) == 0:
                # Last chunk, break the loop
                break
            chunk_number += 1

    def restart(self) -> None:
        """
        Restart the io4edge device.
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        """
        cmd = Pb.CoreCommand(id=Pb.CommandId.RESTART)
        self.command(cmd, Pb.CoreResponse())

    def set_persistent_parameter(self, name: str, value: str) -> None:
        """
        Set a persistent parameter on the io4edge device.
        @param name: name of the parameter
        @param value: value of the parameter
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        """
        cmd = Pb.CoreCommand(
            id=Pb.CommandId.SET_PERSISTENT_PARAMETER,
            set_persistent_parameter=Pb.SetPersistentParameterCommand(
                name=name, value=value))
        self.command(cmd, Pb.CoreResponse())

    def get_persistent_parameter(self, name: str) -> str:
        """
        Get a persistent parameter from the io4edge device.
        @param name: name of the parameter
        @return: value of the parameter
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        """
        cmd = Pb.CoreCommand(
            id=Pb.CommandId.GET_PERSISTENT_PARAMETER,
            get_persistent_parameter=Pb.GetPersistentParameterCommand(name=name))
        response = Pb.CoreResponse()
        self.command(cmd, response)
        return response.persistent_parameter.value

    def get_reset_reason(self) -> str:
        """
        Get the reason for the last reset of the io4edge device.
        @return: reset reason as a string
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        """
        cmd = Pb.CoreCommand(id=Pb.CommandId.GET_RESET_REASON)
        response = Pb.CoreResponse()
        self.command(cmd, response)
        return response.reset_reason.reason
