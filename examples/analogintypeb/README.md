# analogInTypeB Examples

## stream.py

Demonstrates streaming of analog input values from multiple channels


On IOU09 or MIO09, supply a voltage between -10V..+10V to the analog input channels you want to use.

Run the demo with:

```
python3 stream.py [--sr <sample-rate>] <function-block-address>
```
e.g.
```
python3 stream.py --sr 2000 S101-IOU09-USB-EXT-1-analogInTypeB
```

To enable stream of specific channels, call the tool with `--channelmask` option, e.g. use mask `0x03` to enable channels 0 and 1:

You can also specify a gain for each channel with `--gain` option, e.g. use `2` to set gain 2x for all channels.


## describe.py

Calls the `describe` function block method to get information about the analog input channels and prints it to the console.

## poll.py

Demonstrates polling of the latest analog input values from multiple channels