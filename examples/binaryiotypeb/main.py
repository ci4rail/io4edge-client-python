#!/usr/bin/env python3
# SPDX-License-Identifer: Apache-2.0
import io4edge_client.binaryiotypeb as binio
import io4edge_client.functionblock as fb
import argparse
import threading
import time




def main():
    parser = argparse.ArgumentParser(description="demo for binary i/o type B client")
    parser.add_argument(
        "addr", help="MDNS address or IP:Port of the function block", type=str
    )
    args = parser.parse_args()

    binio_client = binio.Client(args.addr)
   

    # determine number of channels
    all_pins_mask = (1 << 2) - 1

    # Set first output to true and the second to false
    binio_client.set_output(0,True)
    print("Channel 1: On\n")
    time.sleep(0.5)
    binio_client.set_output(1,False)
    print("Channel 2: Off\n")


    # Set both outputs to true
    binio_client.set_all_outputs(0x3,all_pins_mask)
    print("Channel 1: On\nChannel 2: On\n")
    # Set first output to false and the second to true
    binio_client.set_all_outputs(0x2,all_pins_mask)
    print("Channel 1: Off\nChannel 2: On\n")
    # Set all outputs to False
    binio_client.set_all_outputs(0x0,all_pins_mask)
    print("Both hannels have been turned Off")




if __name__ == "__main__":
    main()
