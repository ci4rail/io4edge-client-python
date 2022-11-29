# canL2 Examples

## config.py

Demonstrates how to configure the bus timing parameters.

Most modules can be configured with a persistent configuration, via the `can-config` parameter. If the persistent configuration is used, the configuration via config.py is not needed.

Example:
```
python3 config.py <function-block-address> --bitrate 1000000 --sample-point 0.75 --sjw 2
```

## send.py

Before calling this example, the `config.py` example should be called to configure the bus timing parameters.

Send a number of CAN test frames. The frames are sent in bursts (called a bucket), and each bucket contains a number of frames. The number of buckets and the number of frames per bucket can be configured.

For example, with the default configuration, the frames are generated as follows:
```
ID=0x100  DATA=
ID=0x100  DATA=01
ID=0x100  DATA=02 02
ID=0x100  DATA=03 03 03
ID=0x100  DATA=04 04 04 04
ID=0x101  DATA=
ID=0x101  DATA=01
ID=0x101  DATA=02 02
ID=0x101  DATA=03 03 03
ID=0x101  DATA=04 04 04 04
ID=0x102  DATA=
...
```

Example:
```
python3 send.py <function-block-address> --messages=10
```

## dumpstream.py

Before calling this example, the `config.py` example should be called to configure the bus timing parameters.

Dumps the received CAN frames to console. By default it will dump all frames, but it can be configured to dump only frames that match a filter (use --acceptancemask and --acceptancecode).
