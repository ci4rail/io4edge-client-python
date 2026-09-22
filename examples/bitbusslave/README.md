# Bitbus slave loopback example

Requires one device with the bitbusSlave and sender-capable bitbusSniffer
function blocks (firmware with the refactored slave API). No Bitbus wiring or
external master is needed.

Run from the repository root, supplying the two function block mDNS names or
IP:port endpoints of the same device:

```sh
python examples/bitbusslave/loopback.py <slave-endpoint> <sniffer-endpoint>
```

For example, using IP addresses and ports:
```python
python examples/bitbusslave/loopback.py 192.168.210.1:10002 192.168.210.1:10001
```

The example enables internal loopback at 375 kBaud and uses slave address 1
with `idle_response=b"\x00"`. It queues a slave message every 0.2 seconds,
sends a master message every 0.5 seconds, and polls every 50 ms to collect
slave messages. Each received slave INFORMATION frame is acknowledged immediately
with RNR, before another slave message can be queued.
Received INFORMATION fields (including
idle responses) and slave status (once per second) are printed to stdout.
Press Ctrl+C to stop and close both clients.
