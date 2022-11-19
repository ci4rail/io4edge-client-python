from io4edge_client.functionblock import Client as FbClient
import io4edge_client.api.binaryIoTypeC.python.binaryIoTypeC.v1alpha1.binaryIoTypeC_pb2 as BinIoPb


class ChannelConfig:
    def __init__(self, channel, mode, initial_value):
        self.channel = channel
        self.mode = mode
        self.initial_value = initial_value


class WatchdogConfig:
    def __init__(self, timeout, mask):
        self.timeout = timeout
        self.mask = mask


class Client:
    def __init__(self, addr: str):
        self._fb_client = FbClient(addr + "._io4edge_binaryIoTypeC._tcp")

    def upload_configuration(self, channelConfig=None, watchdogConfig=None):
        fs_cmd = BinIoPb.ConfigurationSet()
        if channelConfig is not None:
            for cfg in channelConfig:
                fs_cmd.channelConfig.add(
                    channel=cfg.channel, mode=cfg.mode, initialValue=cfg.initial_value
                )
        if watchdogConfig is not None:
            fs_cmd.outputWatchdogMask = watchdogConfig.mask
            fs_cmd.outputWatchdogTimeout = watchdogConfig.timeout
        self._fb_client.upload_configuration(fs_cmd)

    def set_output(self, channel: int, state: bool):
        fs_cmd = BinIoPb.FunctionControlSet()
        fs_cmd.single.channel = channel
        fs_cmd.single.state = state
        self._fb_client.function_control_set(fs_cmd)

    def close(self):
        self._fb_client.close()
