#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
import io4edge_client.binaryiotypec as binio
import io4edge_client.functionblock as fb
import argparse
import threading
import time


def main():
    parser = argparse.ArgumentParser(description="demo for binary i/o type c client")
    parser.add_argument(
        "addr", help="MDNS address or IP:Port of the function block", type=str
    )
    args = parser.parse_args()

    binio_client = binio.Client(args.addr)

    # determine number of channels
    n_channels = binio_client.describe().numberOfChannels
    print("Number of channels in function block", n_channels)

    n_outputs = int(n_channels / 2)

    config = binio.Pb.ConfigurationSet()
    for channel in range(n_outputs):
        config.channelConfig.add(
            channel=channel,
            mode=binio.Pb.ChannelMode.BINARYIOTYPEC_OUTPUT_PUSH_PULL,
            initialValue=False,
        )
    config.outputWatchdogMask = (1 << n_outputs) - 1
    config.outputWatchdogTimeout = 1000
    binio_client.upload_configuration(config)

    config = binio_client.download_configuration()
    print("Downloaded config is", config)

    # Start a thread that will stimulate the outputs
    threading.Thread(
        target=stim_thread, daemon=True, args=(binio_client, n_outputs)
    ).start()

    binio_client.start_stream(
        binio.Pb.StreamControlStart(channelFilterMask=0xFFFF),
        fb.Pb.StreamControlStart(
            bucketSamples=25,
            keepaliveInterval=1000,
            bufferedSamples=50,
            low_latency_mode=True,
        ),
    )

    # demonstrate how to read single or all channels
    for _ in range(10):
        state, diag = binio_client.input(0)
        print("Reading Ch0 state=%d diag=0x%x" % (state, diag))

        all = binio_client.all_inputs()
        for channel in range(n_channels):
            state = 1 if all.inputs & (1 << channel) else 0
            print("  Ch%d state=%d diag=0x%x" % (channel, state, all.diag[channel]))

        time.sleep(0.5)

    # demonstrate how to read stream
    for _ in range(10):
        generic_stream_data, stream_data = binio_client.read_stream()
        print(
            f"Received stream data {generic_stream_data.deliveryTimestampUs}, {generic_stream_data.sequence}"
        )
        for sample in stream_data.samples:
            print(" Inputs=0x%x Valid=0x%x" % (sample.values, sample.value_valid))

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
