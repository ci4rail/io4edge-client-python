# SPDX-License-Identifer: Apache-2.0
from io4edge_client.functionblock import Client as FbClient
import io4edge_client.api.canL2.python.canL2.v1alpha1.canL2_pb2 as Pb
import io4edge_client.api.io4edge.python.functionblock.v1alpha1.io4edge_functionblock_pb2 as FbPb


class Client:
    """
    canL2 (CAN Layer2) functionblock client.
    @param addr: address of io4edge function block (mdns name or "ip:port" address)
    @param command_timeout: timeout for commands in seconds
    """

    def __init__(self, addr: str, command_timeout=5):
        self._fb_client = FbClient("_io4edge_canL2._tcp", addr, command_timeout)

    def upload_configuration(self, config: Pb.ConfigurationSet):
        """
        Upload the configuration to the canL2 functionblock.
        @param config: configuration to upload
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        """
        self._fb_client.upload_configuration(config)

    def download_configuration(self) -> Pb.ConfigurationGetResponse:
        """
        Download the configuration from the canL2 functionblock.
        @return: actual configuration
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        """
        fs_response = Pb.ConfigurationGetResponse()
        self._fb_client.download_configuration(Pb.ConfigurationGet(), fs_response)
        return fs_response

    def send_frames(self, frames):
        """
        Send frames to the CAN bus. if the queue on the device is not large enough to contain all frames,
        send nothing and raise temporarily unavailable error.

        @param frames: list of frames to send
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        """
        fs_cmd = Pb.FunctionControlSet(frame=frames)
        self._fb_client.function_control_set(fs_cmd, Pb.FunctionControlSetResponse())

    def ctrl_state(self):
        """
        Get the current state of the CAN controller.
        @return: current state of the CAN controller
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        """
        fs_cmd = Pb.FunctionControlGet()
        fs_response = Pb.FunctionControlGetResponse()
        self._fb_client.function_control_get(fs_cmd, fs_response)
        return fs_response.controllerState

    def start_stream(
        self, config: Pb.StreamControlStart, fb_config: FbPb.StreamControl
    ):
        """
        Start streaming of CAN data.
        @param config: CAN specific filter configuration of the stream
        @param fb_config: functionblock generic configuration of the stream
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        """
        self._fb_client.start_stream(config, fb_config)

    def stop_stream(self):
        """
        Stop streaming of CAN data.
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        """
        self._fb_client.stop_stream()

    def read_stream(self, timeout=None):
        """
        Read the next message from the stream.
        @param timeout: timeout in seconds
        @return: functionblock generic stream data (deliveryTimestampUs, sequence), CAN specific stream data
        @raises TimeoutError: if no data is available within the timeout
        """
        stream_data = Pb.StreamData()
        generic_stream_data = self._fb_client.read_stream(timeout, stream_data)
        return generic_stream_data, stream_data

    def close(self):
        """
        Close the connection to the function block, terminate read thread.
        After calling this method, the object is no longer usable.
        """
        self._fb_client.close()
