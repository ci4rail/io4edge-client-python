#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
import io4edge_client.programmablePsu as psu
import argparse
import time
from google.protobuf import timestamp_pb2


def main():
    parser = argparse.ArgumentParser(
        description="demo for calibration of programmable PSU client"
    )
    parser.add_argument(
        "addr", help="MDNS address or IP:Port of the function block", type=str
    )
    args = parser.parse_args()

    psu_client = psu.Client(args.addr)

    desc = psu_client.describe()
    print(f"PSU Capabilities:\n{desc}")
    
    calib = psu_client.get_calibration()
    print(f"Current Calibration: {calib}")
    
    ts = timestamp_pb2.Timestamp()
    ts.GetCurrentTime()
    
    calib.dac_voffs = 0.01
    calib.dac_vgain = 1.001
    calib.calibration_date.CopyFrom(ts)
    psu_client.set_calibration(calib)

    calib = psu_client.get_calibration()
    print(f"New Calibration: {calib}")
    print(f"Calibration Date: {calib.calibration_date.ToDatetime().isoformat()}")


if __name__ == "__main__":
    main()
