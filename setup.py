# SPDX-License-Identifer: Apache-2.0
from setuptools import setup, find_packages
import os
import re


def read(fname):
    try:
        return open(os.path.join(os.path.dirname(__file__), fname)).read()
    except IOError:
        return "File '%s' not found.\n" % fname


def readVersion():
    txt = read("io4edge_client/version.py")
    ver = re.findall(r"([0-9]+), ([0-9]+), ([0-9]+)", txt)
    ver = ver[0]
    print("ver=%s" % ver.__str__())
    return ver[0] + "." + ver[1] + "." + ver[2]


def find_all_pbs():
    all_pbs = []
    for root, dirs, files in os.walk("io4edge_client"):
        for file in files:
            if file.endswith("_pb2.py"):
                path = os.path.join(root, file)
                path = os.sep.join(path.split(os.sep)[1:])
                all_pbs.append(path)
    return all_pbs


setup(
    name="io4edge_client",
    install_requires=[
        "protobuf",
        "zeroconf",
    ],
    version=readVersion(),
    description="A python library for io4edge devices",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    url="https://github.com/ci4rail/io4edge-client-python",
    project_urls={
        "Source Code": "https://github.com/ci4rail/io4edge-client-python.git",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    author="Ci4Rail GmbH",
    author_email="engineering@ci4rail.com",
    license_files="LICENSE",
    packages=find_packages(where="."),
    package_data={"io4edge_client": find_all_pbs()},
    setup_requires=["wheel"],
)
