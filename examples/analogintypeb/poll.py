#!/usr/bin/env python3
# SPDX-License-Identifer: Apache-2.0
import io4edge_client.analogintypeb as ana
import argparse
import time

def main():
    parser = argparse.ArgumentParser(description="demo for values() function of analog in type B client")
    parser.add_argument(
        "addr", help="MDNS address or IP:Port of the function block", type=str
    )
    args = parser.parse_args()

    ana_client = ana.Client(args.addr)
    
    while(True):
        values = ana_client.value()
        ch = 0
        for value in values:
            print(f"Ch{ch}: {value: .3f}")
            ch += 1
        print("----------------")
        time.sleep(1)


if __name__ == "__main__":
    main()
