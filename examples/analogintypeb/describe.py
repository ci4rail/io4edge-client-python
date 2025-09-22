#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
import io4edge_client.analogintypeb as ana
import io4edge_client.functionblock as fb
import argparse


def main():
    parser = argparse.ArgumentParser(
        description="demo for describe function of analog in type B client"
    )
    parser.add_argument(
        "addr", help="MDNS address or IP:Port of the function block", type=str
    )
    args = parser.parse_args()

    ana_client = ana.Client(args.addr)
    specs = ana_client.describe()
    print("Function block specs:", specs)


if __name__ == "__main__":
    main()
