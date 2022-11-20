import io4edge_client.binaryiotypec as binio
import io4edge_client.functionblock as fb
import threading
import time


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

    # Crashed due to bug in IOU07
    # config = binio_client.download_configuration()
    # print("Downloaded config is", config)

    threading.Thread(target=stim_thread, daemon=True, args=(binio_client,)).start()

    binio_client.start_stream(
        binio.Pb.StreamControlStart(channelFilterMask=0xFFFF),
        fb.Pb.StreamControlStart(
            bucketSamples=25,
            keepaliveInterval=1000,
            bufferedSamples=50,
            low_latency_mode=True,
        ),
    )

    while True:
        generic_stream_data, stream_data = binio_client.read_stream()
        print(
            f"Received stream data {generic_stream_data.deliveryTimestampUs}, {generic_stream_data.sequence}\n{stream_data}"
        )


def stim_thread(binio_client):
    while True:
        binio_client.set_output(1, True)
        time.sleep(0.3)
        binio_client.set_output(1, False)
        time.sleep(0.3)


if __name__ == "__main__":
    main()
