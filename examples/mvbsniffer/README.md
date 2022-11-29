# mvbSniffer Examples

## dumpstream.py

Dumps the received MVB frames to console. It will dump all frames, except timed out frames (master frames without an answer from the slave).

Example:
```
python3 dumpstream.py <function-block-address>
```

If you don't have a real MVB bus, you can use the internal generator of the MVB sniffer to generate some test frames. Enable the generator with the `--gen` parameter.

Example:
```
python3 dumpstream.py <function-block-address> --gen
```
