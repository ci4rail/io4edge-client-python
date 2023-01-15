# analogInTypeA Examples

## main.py

Demonstrates streaming of analog input values.


On IOU01 or MIO01, supply a voltage between -10V..+10V to the analog input channel you want to use.

Run the demo with:

```
python3 main.py [--sr <sample-rate>] <function-block-address>
```
e.g.
```
python3 main.py --sr 2000 S101-IOU01-USB-EXT-1-analogInTypeA1
```
