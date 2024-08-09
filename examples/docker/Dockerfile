
FROM ubuntu:22.04

RUN apt-get update && apt-get install -y --no-install-recommends iputils-ping ca-certificates python3 python3-pip

RUN pip install zeroconf protobuf
RUN pip install io4edge-client>=1.0.2
COPY examples/mvbsniffer/dumpstream.py /bin

ENTRYPOINT ["python3", "/bin/dumpstream.py"]
CMD ["-h"]
