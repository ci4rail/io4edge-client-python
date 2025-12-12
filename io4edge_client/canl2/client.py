# SPDX-License-Identifier: Apache-2.0
from typing import List
from io4edge_client.base.connections import ClientConnectionStream, connectable
from io4edge_client.base.logging import io4edge_client_logger
from io4edge_client.functionblock import Client as FbClient
import io4edge_client.api.canL2.python.canL2.v1alpha1.canL2_pb2 as Pb


class Client(
    ClientConnectionStream[FbClient, Pb.StreamControlStart, Pb.StreamData]
):
    """
    canL2 (CAN Layer2) functionblock client.
    @param addr: address of io4edge function block (mdns name or "ip:port" address)
    @param command_timeout: timeout for commands in seconds
    """

    def __init__(
        self,
        addr: str,
        command_timeout: int = 5,
        connect: bool = True
    ) -> None:
        self._logger = io4edge_client_logger("canl2.Client")
        self._logger.debug("Initializing canl2 client")
        fb_client = FbClient(
            "_io4edge_canL2._tcp", addr, command_timeout,
            connect=connect
        )
        super().__init__(fb_client)
        # Type hint for better IDE support
        self._client: FbClient = self._client

    def _create_stream_data(self) -> Pb.StreamData:
        """Create canL2-specific StreamData message"""
        return Pb.StreamData()

    def _create_default_stream_config(self) -> Pb.StreamControlStart:
        """Create default canL2-specific StreamControlStart message"""
        return Pb.StreamControlStart()

    @connectable
    def upload_configuration(self, config: Pb.ConfigurationSet) -> None:
        """
        Upload the configuration to the canL2 functionblock.
        @param config: configuration to upload
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        """
        self._logger.debug("Uploading configuration for canl2")
        self._client.upload_configuration(config)

    @connectable
    def download_configuration(self) -> Pb.ConfigurationGetResponse:
        """
        Download the configuration from the canL2 functionblock.
        @return: actual configuration
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        """
        fs_response = Pb.ConfigurationGetResponse()
        self._client.download_configuration(Pb.ConfigurationGet(), fs_response)
        return fs_response

    @connectable
    def send_frames(self, frames: List[Pb.Frame]) -> None:
        """
        Send frames to CAN bus. If device queue lacks capacity,
        send nothing and raise temporarily unavailable error.

        @param frames: list of frames to send
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        """
        fs_cmd = Pb.FunctionControlSet(frame=frames)
        self._client.function_control_set(
            fs_cmd, Pb.FunctionControlSetResponse()
        )

    @connectable
    def ctrl_state(self) -> Pb.ControllerState.ValueType:
        """
        Get the current state of the CAN controller.
        @return: current state of the CAN controller
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        """
        fs_cmd = Pb.FunctionControlGet()
        fs_response = Pb.FunctionControlGetResponse()
        self._client.function_control_get(fs_cmd, fs_response)
        return fs_response.controllerState
