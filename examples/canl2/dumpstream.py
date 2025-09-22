#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
import io4edge_client.canl2 as canl2
import io4edge_client.functionblock as fb
import argparse


def main():
    parser = argparse.ArgumentParser(description="dump stream from canl2")
    parser.add_argument(
        "addr", help="MDNS address or IP:Port of the CANL2 function block", type=str
    )
    parser.add_argument(
        "--acceptancecode",
        help="CAN Filter Acceptance Code",
        type=lambda x: int(x, 0),
        default=0x00000000,
    )
    parser.add_argument(
        "--acceptancemask",
        help="CAN Filter Acceptance Mask",
        type=lambda x: int(x, 0),
        default=0x00000000,
    )
    parser.add_argument(
        "--lowlatency",
        help="Use stream low latency mode",
        action="store_true",
    )
    args = parser.parse_args()

    can_client = canl2.Client(args.addr)

    stream_start = canl2.Pb.StreamControlStart(
        acceptanceCode=args.acceptancecode, acceptanceMask=args.acceptancemask
    )

    can_client.start_stream(
        stream_start,
        fb.Pb.StreamControlStart(
            bucketSamples=100,
            keepaliveInterval=1000,
            bufferedSamples=200,
            low_latency_mode=args.lowlatency,
        ),
    )

    while True:
        try:
            generic_stream_data, stream_data = can_client.read_stream(timeout=3)
        except TimeoutError:
            print("Timeout while reading stream")
            continue

        ctrl_state = can_client.ctrl_state()

        print(
            "Received %d samples, seq=%d ctrl_state=%s"
            % (
                len(stream_data.samples),
                generic_stream_data.sequence,
                canl2.Pb._CONTROLLERSTATE.values_by_number[ctrl_state].name,
            )
        )

        for sample in stream_data.samples:
            print(sample_to_str(sample))


def sample_to_str(sample):
    ret_val = "%10d us: " % sample.timestamp
    if sample.isDataFrame:
        frame = sample.frame
        ret_val += "ID:"
        if frame.extendedFrameFormat:
            ret_val += "%08X" % frame.messageId
        else:
            ret_val += "%03X" % frame.messageId
        if frame.remoteFrame:
            ret_val += " R"
        ret_val += " DATA:"
        for i in range(len(frame.data)):
            ret_val += "%02X " % frame.data[i]
        ret_val += " "

    ret_val += "ERROR: " + canl2.Pb._ERROREVENT.values_by_number[sample.error].name
    ret_val += (
        " STATE: "
        + canl2.Pb._CONTROLLERSTATE.values_by_number[sample.controllerState].name
    )
    return ret_val


if __name__ == "__main__":
    main()
