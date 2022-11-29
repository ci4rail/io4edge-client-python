# binaryIoTypeC Examples

## main.py

Demonstrates all functions of the binaryIoTypeC client.

The first half of the channels is configured as outputs and the second half as inputs.

Please supply all channel groups with supply voltage.
Connect the output channels to the corresponding input channels. For example, on the IOU07, connect channel 0 to channel 8, channel 1 to channel 9, etc.

The outputs are stimulated by a thread to force transitions on the inputs.

Run the demo with:

```
python3 main.py <function-block-address>
```
e.g.
```
python3 main.py S101-IOU07-USB-EXT-1-binio
```
