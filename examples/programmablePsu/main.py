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

    psu_client.set_voltage_level(10)
    psu_client.set_current_limit(0.3)
    psu_client.set_output_enabled(True)

    while True:
        state = psu_client.get_state()
        print(f"           Output State: {psu.Pb.FunctionControlGetResponse.OutputState.Name(state.output_state)}")
        print(f"             Diag Flags: {state.diag_flags}")
        print(f"        Desired Voltage: {state.desired_voltage: .3f} V")
        print(f"Measured Output Voltage: {state.measured_output_voltage: .3f} V")
        print(f" Measured Sense Voltage: {state.measured_sense_voltage: .3f} V")
        print(f"      Set Current Limit: {state.current_limit: .3f} A")
        print(f"       Measured Current: {state.measured_current: .3f} A")
        print(f"            Temperature: {state.temperature: .1f} °C")
        print("--------------------------------")
        
        time.sleep(1)


if __name__ == "__main__":
    main()
