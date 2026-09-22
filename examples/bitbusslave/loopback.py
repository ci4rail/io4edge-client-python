#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exercise a slave and simulated master on one device, without Bitbus wiring."""

import argparse
import time

import io4edge_client.bitbusslave as bbslave
import io4edge_client.bitbussniffer as bbsniffer
import io4edge_client.functionblock as fb


def exchange(sniffer, control, information=b""):
    """Send to slave address 1, skip the local echo, and await its response."""
    command = bytes((1, control)) + information
    sniffer.send_frame(command)
    deadline = time.monotonic() + 3
    echo_seen = False
    while (remaining := deadline - time.monotonic()) > 0:
        _, data = sniffer.read_stream(timeout=remaining)
        for sample in data.samples:
            frame = bytes(sample.bitbus_frame)
            if sample.flags:
                raise RuntimeError(f"Sniffer flags: 0x{sample.flags:x}")
            if frame == command and not echo_seen:
                # An RR reply can be identical to the command: skip only once.
                echo_seen = True
                continue
            if len(frame) >= 2 and frame[0] == 1:
                return frame
    raise TimeoutError("No slave response")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("slave", help="slave function block mDNS name or IP:port")
    parser.add_argument("sniffer", help="sniffer function block mDNS name or IP:port")
    args = parser.parse_args()

    with bbsniffer.Client(args.sniffer) as sniffer, bbslave.Client(args.slave) as slave:
        sniffer.upload_configuration(bbsniffer.Pb.ConfigurationSet(
            baud_62500=False, address_filter=b"\xff" * 32,
            min_frame_length=0, prepare_sender=True,
            loopback_enable=True, full_duplex=True,
        ))
        slave.upload_configuration(bbslave.Pb.ConfigurationSet(
            slave_address=1, baud_62500=False, app_wd_timeout_ms=5000,
            idle_response=b"\x00",
        ))
        for client in (sniffer, slave):
            client.start_stream(fb_config=fb.Pb.StreamControlStart(
                bucketSamples=1, bufferedSamples=64,
                keepaliveInterval=1000, low_latency_mode=True,
            ))

        # DISC may first return FRMR if a previous session left the slave in NRM.
        response = exchange(sniffer, 0x53)
        if response == b"\x01\x97":
            response = exchange(sniffer, 0x53)
        if response != b"\x01\x73" or exchange(sniffer, 0x93) != b"\x01\x73":
            raise RuntimeError("DISC/SNRM handshake failed")

        ns = nr = 0  # Next master transmit / expected slave receive sequence.
        next_slave = next_master = next_status = time.monotonic()
        while True:
            now = time.monotonic()
            if now >= next_slave:
                slave.set_tx_message(b"slave message")
                next_slave = now + 0.2

            # Poll between master messages to collect and acknowledge slave data.
            sending = now >= next_master
            control = (nr << 5) | 0x10 | ((ns << 1) if sending else 0x01)
            response = exchange(sniffer, control, b"master message" if sending else b"")
            if sending:
                ns = (ns + 1) % 8
                next_master = now + 0.5
            control = response[1]
            if control & 1 == 0:  # I frame: acknowledge N(S) in our next request.
                if (control >> 1) & 7 != nr:
                    raise RuntimeError("Unexpected slave sequence number")
                nr = (nr + 1) % 8
                print(f"Master received: {response[2:]!r}", flush=True)
            elif control & 0x0F != 0x01:  # Otherwise only RR is expected.
                raise RuntimeError(f"Unexpected slave response: {response.hex()}")
            if (control >> 5) & 7 != ns:
                raise RuntimeError("Slave did not acknowledge master message")

            # Use the slave API to receive the master's INFORMATION fields.
            while True:
                try:
                    _, data = slave.read_stream(timeout=0)
                except TimeoutError:
                    break
                for sample in data.samples:
                    print(f"Slave received: {sample.bitbus_information!r}", flush=True)

            if now >= next_status:
                state = slave.get_state()
                print(f"Slave status: {bbslave.Pb.SlaveMode.Name(state.mode)}, "
                      f"pending TX={state.have_pending_tx_msg}", flush=True)
                next_status = now + 1
            time.sleep(0.05)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
