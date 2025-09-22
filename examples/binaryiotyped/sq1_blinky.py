#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0

# Test the two binary I/O groups of SQ1 against eachother
# Group 1 operates as output, Group 2 operates as input
# Connect I/O 1 of first group to I/O 1 of second group
# Connect I/O 2 of first group to I/O 2 of second group
# Connect I/O 3 of first group to I/O 3 of second group
# Connect I/O 4 of first group to I/O 4 of second group

import io4edge_client.binaryiotyped as binio
import argparse
import time


def main():
    parser = argparse.ArgumentParser(
        description="Tests the two binary I/O groups of SO1 against eachother"
    )
    parser.add_argument(
        "addr", help="MDNS address or IP:Port of the function block", type=str
    )

    parser.add_argument(
        "--period",
        help="Update period in ms",
        type=int,
        default=500,
    )
    args = parser.parse_args()

    binio_client = binio.Client(args.addr)
    config(binio_client)
    print("Configuration uploaded")

    err_count = 0
    while True:
        for channel in range(4):
            for state in [True, False]:
                binio_client.set_output(channel, state)
                # print(f"Output {channel} set to {state}")
                time.sleep(args.period / 1000)

                err_count += check_channels(
                    binio_client, ((1 if state else 0) << channel)
                )
                print(f"Error count: {err_count}")


def check_channels(binio_client, ch_mask):
    err_count = 0
    expected_inputs = ch_mask + (ch_mask << 4)
    channels = binio_client.get_channels()

    if channels.inputs != expected_inputs:
        print(f"Expected inputs {expected_inputs:02x}, got {channels.inputs:02x}")
        err_count += 1

    for i in range(8):
        if channels.diag[i] != 0:
            print(f"Channel {i} has diagnostic error {channels.diag[i]}")
            err_count += 1
    return err_count


def config(binio_client):

    for channel in range(4):
        binio_client.upload_configuration(
            binio.Pb.ConfigurationSet(
                channelConfig=[
                    binio.Pb.ChannelConfig(
                        channel=channel,
                        mode=2,  # high-active output
                        initialValue=0,
                        overloadRecoveryTimeoutMs=50,
                        watchdogTimeoutMs=2000,
                    )
                ]
            )
        )
    for channel in range(4, 8):
        binio_client.upload_configuration(
            binio.Pb.ConfigurationSet(
                channelConfig=[
                    binio.Pb.ChannelConfig(
                        channel=channel,
                        mode=0,  # high-active input
                        frittingEnable=True,
                    )
                ]
            )
        )


if __name__ == "__main__":
    main()
