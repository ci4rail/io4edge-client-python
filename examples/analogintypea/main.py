#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
import io4edge_client.analogintypea as ana
import io4edge_client.functionblock as fb
import argparse


def main():
    parser = argparse.ArgumentParser(description="demo for analog in type A client")
    parser.add_argument(
        "addr", help="MDNS address or IP:Port of the function block", type=str
    )
    parser.add_argument(
        "--sr",
        help="Sample Rate in Hz",
        type=int,
        default=1000,
    )
    args = parser.parse_args()

    ana_client = ana.Client(args.addr)

    # configure the function block
    config = ana.Pb.ConfigurationSet(sample_rate=args.sr)
    ana_client.upload_configuration(config)

    # read back the configuration
    config = ana_client.download_configuration()
    print("Downloaded config is", config)

    ana_client.start_stream(
        fb.Pb.StreamControlStart(
            bucketSamples=100,
            keepaliveInterval=1000,
            bufferedSamples=200,
            low_latency_mode=False,
        ),
    )

    # demonstrate how to read stream
    n = 0
    while True:
        generic_stream_data, stream_data = ana_client.read_stream()
        print(
            f"Received stream data {generic_stream_data.deliveryTimestampUs}, {generic_stream_data.sequence}"
        )
        for sample in stream_data.samples:
            print(" #%d: ts=%d %.4f" % (n, sample.timestamp, sample.value))
            n += 1

    # not reached
    # ana_client.stop_stream()
    # ana_client.close()


if __name__ == "__main__":
    main()
