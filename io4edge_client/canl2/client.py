# SPDX-License-Identifier: Apache-2.0
from io4edge_client.base.connections import ClientConnectionStream, connectable
from io4edge_client.functionblock import Client as FbClient
import io4edge_client.api.canL2.python.canL2.v1alpha1.canL2_pb2 as Pb


class Client(ClientConnectionStream[Pb.StreamControlStart, Pb.StreamData]):
    """
    canL2 (CAN Layer2) functionblock client.
    @param addr: address of io4edge function block (mdns name or "ip:port" address)
    @param command_timeout: timeout for commands in seconds
    """

    def __init__(self, addr: str, command_timeout=5, connect=True):
        super().__init__(FbClient("_io4edge_canL2._tcp", addr, command_timeout, connect=connect))

    def _create_stream_data(self) -> Pb.StreamData:
        """Create canL2-specific StreamData message"""
        return Pb.StreamData()

    def _create_default_stream_config(self) -> Pb.StreamControlStart:
        """Create default canL2-specific StreamControlStart message"""
        return Pb.StreamControlStart()

    @connectable
    def upload_configuration(self, config: Pb.ConfigurationSet):
        """
        Upload the configuration to the canL2 functionblock.
        @param config: configuration to upload
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        """
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
    def send_frames(self, frames):
        """
        Send frames to the CAN bus. if the queue on the device is not large enough to contain all frames,
        send nothing and raise temporarily unavailable error.

        @param frames: list of frames to send
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        """
        fs_cmd = Pb.FunctionControlSet(frame=frames)
        self._client.function_control_set(fs_cmd, Pb.FunctionControlSetResponse())

    @connectable
    def ctrl_state(self):
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
