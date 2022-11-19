import io4edge_client.binaryiotypec as binio
import io4edge_client.api.binaryIoTypeC.python.binaryIoTypeC.v1alpha1.binaryIoTypeC_pb2 as BinIoPb


def main():
    binio_client = binio.client.Client("S101-IOU07-USB-EXT-1-binio")
    binio_client.upload_configuration(
        channelConfig=[
            binio.ChannelConfig(
                0, BinIoPb.ChannelMode.BINARYIOTYPEC_OUTPUT_PUSH_PULL, False
            ),
            binio.ChannelConfig(
                1, BinIoPb.ChannelMode.BINARYIOTYPEC_OUTPUT_PUSH_PULL, False
            ),
        ],
        watchdogConfig=binio.WatchdogConfig(1000, 0xFF),
    )
    binio_client.set_output(1, True)
    binio_client.close()


if __name__ == "__main__":
    main()
