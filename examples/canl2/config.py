#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
import io4edge_client.canl2 as canl2
import argparse


def main():
    parser = argparse.ArgumentParser(description="configure canl2")
    parser.add_argument(
        "addr", help="MDNS address or IP:Port of the CANL2 function block", type=str
    )
    parser.add_argument(
        "--bitrate",
        help="CAN bitrate",
        type=int,
        default=500000,
    )
    parser.add_argument(
        "--samplepoint",
        help="CAN sample point (0.0-1.0)",
        type=float,
        default=0.8,
    )
    parser.add_argument(
        "--sjw",
        help="CAN resynchronization jump width",
        type=int,
        default=1,
    )
    parser.add_argument(
        "--listenonly",
        help="Listen only mode",
        action="store_true",
    )
    args = parser.parse_args()

    can_client = canl2.Client(args.addr)

    can_client.upload_configuration(
        canl2.Pb.ConfigurationSet(
            baud=args.bitrate,
            samplePoint=int(args.samplepoint * 1000),
            sjw=args.sjw,
            listenOnly=args.listenonly,
        )
    )

    print("Configuration uploaded")

    actual_config = can_client.download_configuration()
    print("Actual configuration:\n", actual_config)


if __name__ == "__main__":
    main()
