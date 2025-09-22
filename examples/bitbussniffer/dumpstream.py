#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
import io4edge_client.bitbussniffer as bbsniffer
import io4edge_client.functionblock as fb
import argparse


def main():
    parser = argparse.ArgumentParser(description="dump stream from bitbus sniffer")
    parser.add_argument(
        "addr", help="MDNS address or IP:Port of the bbsniffer function block", type=str
    )
    parser.add_argument(
        "--lowlatency",
        help="Use stream low latency mode",
        action="store_true",
    )
    args = parser.parse_args()

    bb_client = bbsniffer.Client(args.addr)

    bb_client.upload_configuration(
        bbsniffer.Pb.ConfigurationSet(
            ignore_crc=True,
            baud_62500=False,
            address_filter=bytes([0xFF] * 32),
        )
    )
    bb_client.start_stream(
        fb.Pb.StreamControlStart(
            bucketSamples=20,
            keepaliveInterval=1000,
            bufferedSamples=60,  # Minimum frames with max. length to buffer. If frames are small, much more frames are buffered
            low_latency_mode=args.lowlatency,
        ),
    )

    while True:
        try:
            generic_stream_data, stream_data = bb_client.read_stream(timeout=3)
        except TimeoutError:
            print("Timeout while reading stream")
            continue

        print(
            "Received %d samples, seq=%d, ts=%d"
            % (
                len(stream_data.samples),
                generic_stream_data.sequence,
                generic_stream_data.deliveryTimestampUs,
            )
        )

        for sample in stream_data.samples:
            print(sample_to_str(sample))


def sample_to_str(sample):
    ret_val = "%10d us: " % sample.timestamp
    if len(sample.bitbus_frame) >= 2:
        ret_val += f"ADDR: 0x{sample.bitbus_frame[0]:02X} "
        ret_val += f"CTRL: 0x{sample.bitbus_frame[1]:02X} "
        ret_val += "INFO: "
        for i in range(2, len(sample.bitbus_frame)):
            ret_val += "%02X " % sample.bitbus_frame[i]

    if sample.flags != bbsniffer.Pb.Sample.Flags.none:
        if sample.flags & bbsniffer.Pb.Sample.Flags.bad_crc:
            ret_val += " CRC_ERR"
        if sample.flags & bbsniffer.Pb.Sample.Flags.frames_lost:
            ret_val += " LOST"
        if sample.flags & bbsniffer.Pb.Sample.Flags.buf_overrun:
            ret_val += " BUF_OVERRUN"

    return ret_val


if __name__ == "__main__":
    main()
