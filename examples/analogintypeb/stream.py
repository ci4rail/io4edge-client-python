#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
import io4edge_client.analogintypeb as ana
import io4edge_client.functionblock as fb
import argparse
import datetime


def highest_bit_set(x: int) -> int:
    """Return the highest bit set in x, or -1 if x is 0"""
    if x == 0:
        return -1
    hb = 0
    while x != 0:
        x >>= 1
        hb += 1
    return hb - 1


def main():
    parser = argparse.ArgumentParser(description="demo for analog in type B client")
    parser.add_argument(
        "addr", help="MDNS address or IP:Port of the function block", type=str
    )
    parser.add_argument(
        "--sr",
        help="Sample Rate in Hz",
        type=float,
        default=1000,
    )
    parser.add_argument(
        "--channelmask",
        help="Channel mask to use",
        type=int,
        default=0xFF,
    )
    parser.add_argument(
        "--gain",
        help="Channel gain",
        type=int,
        default=1,
    )
    parser.add_argument(
        "--dumpsamples",
        help="Dump all samples to console",
        action="store_true",
    )

    args = parser.parse_args()

    highest_channel = highest_bit_set(args.channelmask)
    if highest_channel < 0:
        print("Error: channelmask must have at least one bit set")
        return

    ana_client = ana.Client(args.addr)

    # configure channels according to channelmask
    config = ana.Pb.ConfigurationSet()
    for channel in range(highest_channel + 1):
        if (args.channelmask & (1 << channel)) != 0:
            config.channelConfig.add(
                channel=channel, sample_rate=args.sr, gain=args.gain
            )

    ana_client.upload_configuration(config)

    # read back the configuration
    config = ana_client.download_configuration()
    print("channel config is", config)

    ana_client.start_stream(
        args.channelmask,
        fb.Pb.StreamControlStart(
            bucketSamples=400,
            keepaliveInterval=1000,
            bufferedSamples=1000,
            low_latency_mode=False,
        ),
    )

    # demonstrate how to read stream
    n = 0
    while True:
        generic_stream_data, stream_data = ana_client.read_stream()
        print(
            f"Received stream data {datetime.datetime.now()} {generic_stream_data.deliveryTimestampUs}, {generic_stream_data.sequence}"
        )
        if args.dumpsamples:
            for sample in stream_data.samples:
                print(
                    " #%d: ts=%d ch %d %s"
                    % (n, sample.timestamp, sample.baseChannel, sample.value)
                )
                n += 1
        else:
            n += len(stream_data.samples)

        if n >= 10000:
            break

    ana_client.stop_stream()
    ana_client.close()


if __name__ == "__main__":
    main()
