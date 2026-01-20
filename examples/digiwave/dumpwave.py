#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
import io4edge_client.digiwave as dw
import io4edge_client.functionblock as fb
import argparse


def transitions_to_vcd(data: list) -> str:
    vcd = """$timescale
1 ns
$end
$var wire 1 ! rx $end
$upscope $end
$enddefinitions $end
"""
    for entry in data:
        time_ns, val = entry
        vcd += f"#{time_ns}\n{1 if val else 0}!\n"
    vcd += """
$dumpoff
$end
"""
    return vcd


# generate a list of transitions, each with a tuple (time, rxvalue)
# time in ns
# rxvalue boolean
def edr_to_transitions(edr: bytes) -> list:
    cur_val = None
    seg_time = 0
    transitions = []

    idx = 0
    for entry in edr:
        if entry & 0x7F == 0:
            # no transition, timeout
            seg_time += 128
        else:
            seg_time += entry & 0x7F
            cur_val = True if entry & 0x80 else False
            if idx == 0:
                seg_time = 0
            transitions.append((seg_time * 250, not cur_val))
            idx += 1

    return transitions


def main():
    parser = argparse.ArgumentParser(description="dump digiwave stream")
    parser.add_argument(
        "addr", help="MDNS address or IP:Port of the bbsniffer function block", type=str
    )
    args = parser.parse_args()

    dw_client = dw.Client(args.addr)

    dw_client.upload_configuration(
        dw.Pb.ConfigurationSet(
            full_duplex=True,
            claim_rx=True,
        )
    )

    dw_client.start_stream(
        dw.Pb.StreamControlStart(),
        fb.Pb.StreamControlStart(
            bucketSamples=3,
            keepaliveInterval=1000,
            bufferedSamples=10,
            low_latency_mode=False,
        ),
    )
    edr = bytearray()
    for loop in range(100):
        try:
            generic_stream_data, stream_data = dw_client.read_stream(timeout=3)
        except TimeoutError:
            print("Timeout while reading stream")
            continue

        print(
            "Received %d samples, seq=%d"
            % (len(stream_data.samples), generic_stream_data.sequence)
        )
        for sample in stream_data.samples:
            edr += sample.transitions_block

    transitions = edr_to_transitions(edr)
    vcd = transitions_to_vcd(transitions)
    with open("dump.vcd", "w") as vcd_file:
        vcd_file.write(vcd)


if __name__ == "__main__":
    main()
