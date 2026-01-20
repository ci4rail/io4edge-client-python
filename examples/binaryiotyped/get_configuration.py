#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
import io4edge_client.binaryiotyped as binio
import argparse


def main():
    parser = argparse.ArgumentParser(
        description="Get binary i/o type D configuration client"
    )
    parser.add_argument(
        "addr", help="MDNS address or IP:Port of the function block", type=str
    )

    args = parser.parse_args()

    binio_client = binio.Client(args.addr)

    config = binio_client.download_configuration()
    print("Downloaded config is :")
    for i in range(len(config.channelConfig)):
        print(
            f"Channel                      : {config.channelConfig[i].channel}\n"
            f"Mode                         : {binio.Pb.ChannelMode.Name(config.channelConfig[i].mode)}\n"
            f"Current Value                : {config.channelConfig[i].initialValue}\n"
            f"Overload Recovery Timeout ms : {config.channelConfig[i].overloadRecoveryTimeoutMs}\n"
            f"Watchdog Timeout ms          : {config.channelConfig[i].watchdogTimeoutMs}\n"
            f"Fritting Enable              : {config.channelConfig[i].frittingEnable}\n"
        )


if __name__ == "__main__":
    main()
