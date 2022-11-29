# io4edge-client-python
python client sdk for io4edge.

[io4edge devices](https://docs.ci4rail.com/edge-solutions/io4edge/) are intelligent I/O devices invented by [Ci4Rail](https://www.ci4rail.com), connected to the host via network.

This library provides support for the following function blocks within io4edge devices:
* CAN Layer2 - IOU03, MIO03, IOU04, MIO04, IOU06
* MVB Sniffer - IOU03, MIO03
* Binary IO TypeC - IOU07 (alpha)

Currently not supported, but will follow:
* Analog In TypeA - IOU01, MIO01
* Binary IO TypeA - IOU01, MIO01
* Binary IO TypeB - IOU06
* Motion Sensor - CPU01UC

Not planned: Support for io4edge management functions, such as firmware update. Please use io4edge-client-go for this.


## Installation

```bash
pip3 install io4edge_client
```

### Usage

See [examples in github repo](https://github.com/ci4rail/io4edge-client-python) for usage examples.

## Copyright

Copyright © 2021-2022 Ci4Rail GmbH <engineering@ci4rail.com>

io4edge_client_python package is released under Apache 2.0 License, see [LICENSE](LICENSE) for details.
