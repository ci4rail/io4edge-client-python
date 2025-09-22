#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
#
# Parse a waveform from CSV file and send it to a Digiwave function block
#
# Expected CSV format:
#
# Header line (skipped):
# 0.000000000;1
# 0.000139952;0

import io4edge_client.digiwave as dw
import io4edge_client.functionblock as fb
import argparse
import csv


def parse_csv_to_dict(file_path):
    data = []
    with open(file_path, "r") as csvfile:
        csv_reader = csv.reader(csvfile, delimiter=";")
        next(csv_reader)  # Skip header

        line = 0
        for row in csv_reader:
            if len(row) == 0:
                break

            entry = {
                "time_s": row[0],
                "value": row[1],
            }
            line += 1
            data.append(entry)

    return data


def entries_to_vcd(data):
    vcd = """$timescale
1 ns
$end
$var wire 1 ! bitbus $end
$upscope $end
$enddefinitions $end
"""
    for entry in data:
        time_ns = float(entry["time_s"]) * 1e9
        if time_ns is not None:
            vcd += f"#{round(time_ns)}\n{entry['value']}!\n"
    vcd += """
$dumpoff
$end
"""
    return vcd


def entries_to_edr(data):
    edr = []
    prev_time = float(data[0]["time_s"])
    i = 0
    for entry in data[1:]:
        dt = (float(entry["time_s"]) - prev_time) * 1e9
        dt /= 250
        dt_before_round = dt
        dt = int(round(dt))
        prev_time = prev_time + dt * 250 / 1e9
        level = 1 if entry["value"] == "1" else 0
        # print(f"{prev_time} dt: {dt}, level: {level}")
        while True:
            if dt == 0:
                break
            if dt >= 0x80:
                v = 0
                dt -= 0x80
            else:
                v = dt & 0x7F
                dt -= v
            if not level:
                v |= 0x80
            # print(f" {i}: v: {v}")
            edr.append(v)
            i += 1
            if dt == 0:
                break

    return edr


def main():
    parser = argparse.ArgumentParser(description="send digiwave stream")
    parser.add_argument(
        "addr", help="MDNS address or IP:Port of the bbsniffer function block", type=str
    )
    parser.add_argument("wavecsv", help="CSV file with waveform", type=str)

    args = parser.parse_args()

    dw_client = dw.Client(args.addr)

    dw_client.upload_configuration(
        dw.Pb.ConfigurationSet(
            full_duplex=True,
            claim_rx=False,
        )
    )

    data = parse_csv_to_dict(args.wavecsv)
    edr = entries_to_edr(data)
    vcd = entries_to_vcd(data)
    with open(args.wavecsv + ".vcd", "w") as vcd_file:
        vcd_file.write(vcd)

    print(len(edr))

    # send edr in chunks of 3000 bytes
    for i in range(0, len(edr), 3000):
        chunk = edr[i : i + 3000]
        dw_client.send_wave(bytes(chunk))
        print(f"Sent {len(chunk)} bytes")


if __name__ == "__main__":
    main()
