#!/usr/bin/env python3
# SPDX-License-Identifer: Apache-2.0
import io4edge_client.binaryiotypeb as binio
import io4edge_client.functionblock as fb
import argparse
import threading
import time


def main():
    parser = argparse.ArgumentParser(description="demo for binary i/o type B client")
    parser.add_argument(
        "addr", help="MDNS address or IP:Port of the function block", type=str
    )
    args = parser.parse_args()

    binio_client = binio.Client(args.addr)

    # determine number of channels
    n_channels = binio_client.describe().numberOfChannels
    print("Number of channels in function block", n_channels)

    all_pins_mask = (1 << n_channels) - 1

    # configure the function block
    config = binio.Pb.ConfigurationSet(outputFrittingMask=all_pins_mask,
                                       outputWatchdogMask=all_pins_mask,
                                       outputWatchdogTimeout=1000)
    binio_client.upload_configuration(config)

    # read back the configuration
    config = binio_client.download_configuration()
    print("Downloaded config is", config)

    # Start a thread that will stimulate the outputs
    threading.Thread(
        target=stim_thread, daemon=True, args=(binio_client, n_channels)
    ).start()

    binio_client.start_stream(
        binio.Pb.StreamControlStart(channelFilterMask=all_pins_mask),
        fb.Pb.StreamControlStart(
            bucketSamples=25,
            keepaliveInterval=1000,
            bufferedSamples=50,
            low_latency_mode=True,
        ),
    )

    # demonstrate how to read single or all channels
    for _ in range(50):
        state = binio_client.input(0)
        print("Reading Ch0 state=%d" % (state))

        all = binio_client.all_inputs(all_pins_mask)
        for channel in range(n_channels):
            state = 1 if all & (1 << channel) else 0
            print("  Ch%d state=%d" % (channel, state))

        time.sleep(0.1)

    # demonstrate how to read stream
    for _ in range(10):
        generic_stream_data, stream_data = binio_client.read_stream()
        print(
            f"Received stream data {generic_stream_data.deliveryTimestampUs}, {generic_stream_data.sequence}"
        )
        for sample in stream_data.samples:
            print(" Channel %d -> %d" % (sample.channel, sample.value))

    binio_client.stop_stream()
    binio_client.close()


def stim_thread(binio_client, n_outputs):
    while True:
        for channel in range(n_outputs):
            binio_client.set_output(channel, True)
            time.sleep(0.3)
            binio_client.set_output(channel, False)
            time.sleep(0.3)


if __name__ == "__main__":
    main()
