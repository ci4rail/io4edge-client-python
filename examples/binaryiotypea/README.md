# binaryIoTypeA Examples

## main.py

Demonstrates most functions of the binaryIoTypeA client.

Each channel's output is read back on the same channel's input. So you only need to supply all channel groups with supply voltage.

The outputs are stimulated by a thread to force transitions on the inputs.

Run the demo with:

```
python3 main.py <function-block-address>
```
e.g.
```
python3 main.py S101-IOU01-USB-EXT-1-binaryIoTypeA
```
