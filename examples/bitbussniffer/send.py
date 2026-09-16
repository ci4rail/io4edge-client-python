#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
import argparse

import io4edge_client.bitbussniffer as bbsniffer


def parse_byte(value: str) -> int:
    parsed_value = int(value, 0)
    if not 0 <= parsed_value <= 0xFF:
        raise argparse.ArgumentTypeError("must be between 0 and 255")
    return parsed_value


def main() -> None:
    parser = argparse.ArgumentParser(description="send a frame to bitbus")
    parser.add_argument(
        "addr", help="MDNS address or IP:Port of the bitbus sniffer", type=str
    )
    parser.add_argument("address", type=parse_byte, help="bitbus address byte")
    parser.add_argument("control", type=parse_byte, help="bitbus control byte")
    parser.add_argument(
        "information",
        help="information bytes as hexadecimal, for example 0102a0",
        default="",
        nargs="?",
    )
    args = parser.parse_args()

    try:
        information = bytes.fromhex(args.information)
    except ValueError as error:
        parser.error(f"information is not valid hexadecimal: {error}")

    client = bbsniffer.Client(args.addr)
    try:
        client.upload_configuration(
            bbsniffer.Pb.ConfigurationSet(prepare_sender=True)
        )
        client.send_frame(bytes([args.address, args.control]) + information)
        print("frame sent")
    finally:
        client.close()


if __name__ == "__main__":
    main()
