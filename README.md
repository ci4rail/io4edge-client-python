# io4edge-client-python
python client sdk for io4edge.

[io4edge devices](https://docs.ci4rail.com/edge-solutions/io4edge/) are intelligent I/O devices invented by [Ci4Rail](https://www.ci4rail.com), connected to the host via network.

This library provides support for the following function blocks within io4edge devices:
* [Binary IO TypeC](io4edge_python/binaryiotypec) - IOU07
* [CAN Layer2](io4edge_python/canl2) - IOU04, MIO04, IOU03, MIO03, IOU06
* [MVB Sniffer](io4edge_python/mvbsniffer) - IOU03, MIO03

Currently not supported, but will follow:
* [Analog In TypeA](io4edge_python/analogintypea) - IOU01, MIO01
* [Binary IO TypeA](io4edge_python/binaryiotypea) - IOU01, MIO01
* [Binary IO TypeB](io4edge_python/binaryiotypeb) - IOU06
* [Motion Sensor](io4edge_python/motionsensor) - CPU01UC

Not planned: Support for io4edge management functions, such as firmware update. Please use io4edge-client-go for this.


## Installation

```bash
pip3 install io4edge_client
```

### Usage

See [examples](examples) for usage examples.

## Copyright

Copyright © 2021-2022 Ci4Rail GmbH <engineering@ci4rail.com>

io4edge_client_python package is released under Apache 2.0 License, see [LICENSE](LICENSE) for details.
