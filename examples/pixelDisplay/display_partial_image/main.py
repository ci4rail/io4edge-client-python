#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
from PIL import Image
import io4edge_client.pixelDisplay as pixdisp
import argparse
import time


def main():
    parser = argparse.ArgumentParser(description="Example for pixel display client")
    parser.add_argument(
        "addr", help="MDNS address or IP:Port of the function block", type=str
    )
    args = parser.parse_args()

    pixdisp_client = pixdisp.Client(args.addr)

    # parse pixel data from jpeg file
    img = Image.open("../test.jpg")
    pix = img.load()
    img1 = Image.open("../partial_test1.jpg")
    pix1 = img1.load()
    img2 = Image.open("../partial_test2.jpg")
    pix2 = img2.load()

    # Set pixel area and set 16 lines at a time
    for i in range(0, 320, 20):
        pix_area = []
        for k in range(0, 20):
            for j in range(0, 240):
                pix_area.append(pix[j, i + k])
        pixdisp_client.set_pixel_area(0, i, 239, pix_area)

    pic = 1
    while True:
        if pic == 1:
            for i in range(0, 60, 20):
                pix_area = []
                for k in range(0, 20):
                    for j in range(0, 40):
                        pix_area.append(pix1[j, i + k])
                pixdisp_client.set_pixel_area(20, i + 200, 59, pix_area)

        if pic == 2:
            for i in range(0, 60, 20):
                pix_area = []
                for k in range(0, 20):
                    for j in range(0, 40):
                        pix_area.append(pix2[j, i + k])
                pixdisp_client.set_pixel_area(20, i + 200, 59, pix_area)

        pic = pic + 1
        if pic > 2:
            pic = 1
        time.sleep(1)


if __name__ == "__main__":
    main()
