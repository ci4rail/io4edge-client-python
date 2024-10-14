#!/usr/bin/env python3
# SPDX-License-Identifer: Apache-2.0
import io4edge_client.binaryiotyped as binio
import argparse

def main():
    parser = argparse.ArgumentParser(description="set output with binary i/o type D client")
    parser.add_argument(
        "addr", help="MDNS address or IP:Port of the function block", type=str
    )
    parser.add_argument(
        "channel", help="Channel number to set", type=int
    )
    parser.add_argument(
        "state", help="State to set (0=inactive, 1=active)", type=int
    )

    args = parser.parse_args()

    binio_client = binio.Client(args.addr)

    binio_client.set_output(args.channel, args.state)
    print(f"Output {args.channel} set to {args.state}")

if __name__ == "__main__":
    main()
