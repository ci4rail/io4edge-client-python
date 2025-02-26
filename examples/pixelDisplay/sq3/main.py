#!/usr/bin/env python3
# SPDX-License-Identifer: Apache-2.0
from PIL import Image
import io4edge_client.pixelDisplay as pixdisp
import io4edge_client.binaryiotypeb as binio
import io4edge_client.functionblock as fb
import argparse
import threading
import time



def main():
    parser = argparse.ArgumentParser(description="todo")
    parser.add_argument(
        "addr", help="MDNS address or IP:Port of the function block", type=str
    )
    args = parser.parse_args()

    pixdisp_client = pixdisp.Client(args.addr + ":10001")
    binio_client = binio.Client(args.addr + ":10002")

    # parse pixel data from jpeg file
    img = Image.open("../test.jpg")
    pix = img.load()

    # Set pixel area and set 16 lines at a time
    for i in range(0, 320, 16):
        pix_area = []
        for k in range (0, 16):
            for j in range(0, 240):
                pix_area.append(pix[j, i+k])
        pixdisp_client.set_pixel_area(0, i, 239, pix_area)

    while True:
        # get input button up state
        if(binio_client.get_input(0) == False):
            print("Button up pressed")
            for i in range(0, 320, 16):
                pix_area = []
                for k in range (0, 16):
                    for j in range(0, 240):
                        pix_area.append(pix[j, i+k])
                pixdisp_client.set_pixel_area(0, i, 239, pix_area)

        # get input button down state
        if(binio_client.get_input(1) == False):
            print("Button down pressed")
            for i in range(319, -1, -16):
                pix_area = []
                for k in range (0, 16):
                    for j in range(239, -1, -1):
                        pix_area.append(pix[j, i-k])
                pixdisp_client.set_pixel_area(0, 319-i, 239, pix_area)

        time.sleep(0.1)


if __name__ == "__main__":
    main()
