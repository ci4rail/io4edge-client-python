#!/usr/bin/env python3
# SPDX-License-Identifer: Apache-2.0
import io4edge_client.canl2 as canl2
import argparse
import time


def main():
    parser = argparse.ArgumentParser(description="send frames to canl2")
    parser.add_argument(
        "addr", help="MDNS address or IP:Port of the CANL2 function block", type=str
    )
    parser.add_argument(
        "--buckets",
        help="Number of buckets to send",
        type=int,
        default=10,
    )
    parser.add_argument(
        "--messages",
        help="Number of messages per bucket",
        type=int,
        default=5,
    )
    parser.add_argument(
        "--gap",
        help="gap between buckets in ms",
        type=int,
        default=0,
    )
    parser.add_argument(
        "--ext",
        help="use extended frames",
        action="store_true",
    )
    parser.add_argument(
        "--rtr",
        help="use RTR frames",
        action="store_true",
    )
    args = parser.parse_args()

    can_client = canl2.Client(args.addr)

    for bucket in range(args.buckets):
        frames = []
        for msg in range(args.messages):
            frames.append(
                canl2.Pb.Frame(
                    messageId=0x100 + bucket % 0xFF,
                    data=bytes([msg for _ in range(msg % 8)]),
                    extendedFrameFormat=args.ext,
                    remoteFrame=args.rtr,
                )
            )
        can_client.send_frames(frames)
        print("sent bucket", bucket)
        time.sleep(args.gap / 1000.0)


if __name__ == "__main__":
    main()
