#!/usr/bin/env python3
# SPDX-License-Identifer: Apache-2.0
import io4edge_client.binaryiotyped as binio
import io4edge_client.functionblock as fb
import argparse

def main():
    parser = argparse.ArgumentParser(description="get channels of binary i/o type D client")
    parser.add_argument(
        "addr", help="MDNS address or IP:Port of the function block", type=str
    )
    args = parser.parse_args()

    binio_client = binio.Client(args.addr)

    res = binio_client.get_channels()
    print(res)
