#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
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

    # start stream
    binio_client.start_stream(
        binio.Pb.StreamControlStart(),
        fb.Pb.StreamControlStart(
            bucketSamples=100,
            keepaliveInterval=1000,
            bufferedSamples=200,
            low_latency_mode=False,
        ),
    )

    while True:
        generic_stream_data, stream_data = binio_client.read_stream()
        print("Generic stream data: ", generic_stream_data)
        for sample in stream_data.samples:
            # print timestamp
            print(f"Timestamp: {sample.timestamp}")
            # iterate bitwiese over the inputs
            for i in range(8):
                if sample.inputs & (1 << i):
                    print(f"Channel {i}: On")
                else:
                    print(f"Channel {i}: Off")


if __name__ == "__main__":
    main()
