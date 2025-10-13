#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
import io4edge_client.programmablePsu as psu
import argparse
import time


def main():
    parser = argparse.ArgumentParser(
        description="demo for values() function of programmable PSU client"
    )
    parser.add_argument(
        "addr", help="MDNS address or IP:Port of the function block", type=str
    )
    args = parser.parse_args()

    psu_client = psu.Client(args.addr)

    psu_client.set_voltage_level(5.0)
    psu_client.set_current_limit(1.0)
    psu_client.set_output_enabled(True)

    while True:
        state = psu_client.get_state()
        print(f"State: {state}")
        time.sleep(1)


if __name__ == "__main__":
    main()
