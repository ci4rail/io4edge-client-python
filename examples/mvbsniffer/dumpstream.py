#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
import io4edge_client.mvbsniffer as mvb
import io4edge_client.functionblock as fb
import argparse

#
# This is a test pattern that generates the following telegrams. Used with --gen option.
# Address    Type                   Data
# 0x001      Process Data 16 Bit    0x01 0x22
# 0x002      Process Data 16 Bit    0x02 0x22
# 0x003      Process Data 16 Bit    0x03 0x22
# 0x004      Process Data 16 Bit    0x04 0x22
# Spacing between telegrams is 106µs
TEST_PATTERN = "034H`@`@`@`@a@`@`Cl@`BbH`@`@`@`@b@`@`Cl@aBbH`@`@`@`@c@`@`Cl@bBbH`@`@`@`@d@`@`Cl@cBbH`@`@`@`@e@a@`Cl@dBb1"


def main():
    parser = argparse.ArgumentParser(description="dump stream from mvb sniffer")
    parser.add_argument(
        "addr", help="MDNS address or IP:Port of the mvb sniffer", type=str
    )
    parser.add_argument(
        "--gen",
        help="Use internal test pattern generator",
        action="store_true",
    )
    args = parser.parse_args()

    mvb_client = mvb.Client(args.addr)

    stream_start = mvb.Pb.StreamControlStart()
    stream_start.filter.add(f_code_mask=0x0FFF, include_timedout_frames=False)

    if args.gen:
        mvb_client.send_pattern(TEST_PATTERN)
    else:
        # ensure we use the external input in case the internal generator has been selected before
        mvb_client.send_pattern("2")

    mvb_client.start_stream(
        stream_start,
        fb.Pb.StreamControlStart(
            bucketSamples=100,
            keepaliveInterval=1000,
            bufferedSamples=200,
            low_latency_mode=False,
        ),
    )

    while True:
        try:
            generic_stream_data, telegrams = mvb_client.read_stream(timeout=3)
        except TimeoutError:
            print("Timeout while reading stream")
            continue

        print(
            "Received %d telegrams, seq=%d"
            % (len(telegrams.entry), generic_stream_data.sequence)
        )
        for telegram in telegrams.entry:
            if telegram.state != mvb.TelegramPb.Telegram.State.kSuccessful:
                if telegram.state & mvb.TelegramPb.Telegram.State.kTimedOut:
                    print("No slave frame has been received to a master frame")
                if telegram.state & mvb.TelegramPb.Telegram.State.kMissedMVBFrames:
                    print(
                        "one or more MVB frames are lost in the device since the last telegram"
                    )
                if telegram.state & mvb.TelegramPb.Telegram.State.kMissedMVBFrames:
                    print("one or more telegrams are lost")
            print(telegram_to_str(telegram))


def telegram_to_str(telegram):
    ret_val = "addr=%03x, " % telegram.address
    ret_val += "%s" % mvb.TelegramPb._TELEGRAM_TYPE.values_by_number[telegram.type].name
    if len(telegram.data) > 0:
        ret_val += ", data="
        for b in telegram.data:
            ret_val += "%02x " % b
    return ret_val


if __name__ == "__main__":
    main()
