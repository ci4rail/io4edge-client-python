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
    parser = argparse.ArgumentParser(description="Example for pixel display client")
    parser.add_argument(
        "addr", help="MDNS address or IP:Port of the function block", type=str
    )
    args = parser.parse_args()

    pixdisp_client = pixdisp.Client(args.addr)

    # test describe pixel display
    describe = pixdisp_client.describe()
    print("hight: ", describe.height_pixel)
    print("width: ", describe.width_pixel)
    print("max pixel number tom transfere at once: ", describe.max_num_of_pixel)

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

    up = True
    while True:
        if up:
            for i in range(0, 320, 16):
                pix_area = []
                for k in range (0, 16):
                    for j in range(0, 240):
                        pix_area.append(pix[j, i+k])
                pixdisp_client.set_pixel_area(0, i, 239, pix_area)

        if not(up):
            # set display off for 3 seconds
            pixdisp_client.set_display_off()
            time.sleep(3)
            # set display on by sending image but this time from bottom to top
            for i in range(319, -1, -16):
                pix_area = []
                for k in range (0, 16):
                    for j in range(239, -1, -1):
                        pix_area.append(pix[j, i-k])
                pixdisp_client.set_pixel_area(0, 319-i, 239, pix_area)

        up = not(up)
        time.sleep(2)


if __name__ == "__main__":
    main()
