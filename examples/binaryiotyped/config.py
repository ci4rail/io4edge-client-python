#!/usr/bin/env python3
# SPDX-License-Identifer: Apache-2.0
import io4edge_client.binaryiotyped as binio
import io4edge_client.functionblock as fb
import argparse

def main():
    parser = argparse.ArgumentParser(description="config binary i/o type D client")
    parser.add_argument(
        "addr", help="MDNS address or IP:Port of the function block", type=str
    )
    parser.add_argument(
        "channel", help="Channel number to configure", type=int
    )
    parser.add_argument(
        "--mode",
        help="Channel mode: 0=high active input, 1=low active input, 2=high-active output, 3=low-active output",
        type=int,
        default=0,
    )
    parser.add_argument(
        "--initactive",
        help="Set initial value to active",
        action="store_true",
    )
    parser.add_argument(
        "--retrytout",
        help="Retry timeout in ms (0=default)",
        type=int,
        default=0,
    )
    parser.add_argument(
        "--wdtout",
        help="Watchdog timeout in ms (0=disable)",
        type=int,
        default=0,
    )
    args = parser.parse_args()

    binio_client = binio.Client(args.addr)

    binio_client.upload_configuration(
        binio.Pb.ConfigurationSet(
            channelConfig=[
                binio.Pb.ChannelConfig(
                    channel=args.channel,
                    mode=args.mode,
                    initialValue=args.initactive,
                    overloadRecoveryTimeoutMs=args.retrytout,
                    watchdogTimeoutMs=args.wdtout,
                )
            ]
        )
    )
    print("Configuration uploaded")

if __name__ == "__main__":
    main()
