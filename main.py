import io4edge_client.binaryiotypec as binio


def main():
    binio_client = binio.client.Client("S101-IOU07-USB-EXT-1-binio")

    config = binio.Pb.ConfigurationSet()
    for channel in range(8):
        config.channelConfig.add(
            channel=channel,
            mode=binio.Pb.ChannelMode.BINARYIOTYPEC_OUTPUT_PUSH_PULL,
            initialValue=False,
        )
    config.outputWatchdogMask = 0x00FF
    config.outputWatchdogTimeout = 1000
    binio_client.upload_configuration(config)

    # config = binio_client.download_configuration()
    # print("Downloaded config is", config)

    binio_client.set_output(1, True)
    binio_client.close()


if __name__ == "__main__":
    main()
