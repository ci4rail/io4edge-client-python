# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

`io4edge-client-python` is the Python client SDK (PyPI package `io4edge_client`) for **io4edge devices** —
intelligent I/O devices invented by Ci4Rail, connected to a host over the network. It implements the *client* side
of the io4edge wire protocol (TCP sockets + protobuf), discovering devices via mDNS or connecting directly by
`IP:port`, and exposes one `Client` class per function block (analog/binary IO, CAN, sensors, LEDs, watchdog,
pixel display, SSM, etc.).

This repo is part of a three-repo workspace alongside `../ekfsm` and `../z1010-cctv` — see
[Relationship to the other repos in this workspace](#relationship-to-the-other-repos-in-this-workspace) below.

## Architecture

Layered under `io4edge_client/`:

- **Base layer** (`io4edge_client/base/`): core networking — mDNS service discovery and socket transport.
- **Functionblock layer** (`io4edge_client/functionblock/`): generic function-block client handling
  command/response and streaming.
- **Device-specific clients**: one directory per function block (`analogintypea/`, `binaryiotypeb/`, `ssm/`,
  `pixelDisplay/`, `colorLED/`, `core/`, etc.), each providing a `Client` class that wraps a `functionblock.Client`.
  `analogintypea/client.py` is the canonical example of the pattern:

  ```python
  class Client:
      def __init__(self, addr: str, command_timeout=5):
          self._fb_client = FbClient("_io4edge_<device_type>._tcp", addr, command_timeout)
  ```

- **Generated APIs** (`io4edge_client/api/`): a **git submodule** (`ci4rail/io4edge_api`) containing the protobuf
  schema and generated Python code for the io4edge protocol. Don't hand-edit generated files here — when `.proto`
  inputs change, regenerate via the `make` workflow documented inside `io4edge_client/api/`.

### Conventions

- mDNS service names follow `_io4edge_<functionblock>._tcp` (e.g. `_io4edge_analogInTypeA._tcp`); addresses are
  either such a service name or `IP:port` (e.g. `"192.168.1.100:9999"`).
- Standard methods across clients: `upload_configuration()` / `download_configuration()`,
  `function_control_set()` / `function_control_get()`, `start_stream()` / `stop_stream()` / `read_stream()`,
  `close()`.
- Streaming uses a producer/consumer pattern: a background thread reads the socket and queues messages;
  `read_stream(timeout=...)` consumes them. Always call `close()` (including in exception handlers) to terminate
  that thread — commands raise `RuntimeError` for protocol errors and `TimeoutError` on command/stream timeouts.
- Import protobuf modules with an explicit `Pb` alias and use absolute imports to avoid conflicts (e.g.
  `import ...analogInTypeA_pb2 as Pb`); use `google.protobuf.any_pb2.Any` for generic message wrapping.
- Adding a new device type: create a module directory under `io4edge_client/`, implement `Client` following the
  established pattern, import its protobuf as `Pb`, add an example under `examples/<device_type>/`, and keep the
  mDNS service name convention.

## Environment & commands

- Requires Python >=3.10. Packaging uses `setuptools` + `setuptools-scm`: the version is derived from git tags —
  never hand-edit `io4edge_client/_version.py`.
- Run checks from the repository root so package discovery and generated API imports match CI.
- **Run tests**: `python -m unittest discover -s tests` (run a single test file first when touching protocol or
  address-handling code, e.g. `python -m unittest tests.test_base`). Tests focus on parsing and address handling
  and must stay independent of physical devices (use local sockets/fixtures); `examples/` double as integration
  references against real or simulated devices.
- Docker examples (`examples/docker/`) require `--network=host` for mDNS discovery — don't silently replace
  service discovery with a hard-coded address.
- **Releasing**: tag with `git tag vX.Y.Z` and `git push --tags`; `.github/workflows/pypi.yaml` handles publishing.

## Relationship to the other repos in this workspace

This workspace holds three repos that together implement one io4edge-based hardware/software stack:

- **`z1010-cctv`** (ESP32-S3 firmware) implements the *server* side of the io4edge protocol for the EKF Z1010
  Chassis Comfort Unit, exposing function blocks (Core, TH sensor, GPIO, LEDs, SSM) over TCP/protobuf, built from
  the same `ci4rail/io4edge_api` protobuf definitions this repo's `io4edge_client/api/` submodule provides.
- **`io4edge-client-python`** (this repo) is the generic client SDK for talking to *any* io4edge device
  (including but not limited to the Z1010 firmware) over that protocol.
- **`ekfsm`** depends on this package (`io4edge_client` in its `pyproject.toml`) and wraps io4edge function-block
  clients as `Device` subclasses in its system tree — see `ekfsm/devices/io4edge.py` (base class, wraps
  `io4edge_client.core.coreclient`), `ekfsm/devices/ssm.py` (wraps `io4edge_client.ssm`), and
  `ekfsm/devices/pixelDisplay.py` (wraps `io4edge_client.pixelDisplay`).

Changing wire-level behavior (protobuf messages, function-block semantics) generally requires coordinated changes
across `io4edge_api` (schema), this repo (client) and, if it's a device also implemented in firmware,
`z1010-cctv`. The Z1010 CCU is *also* reachable via a separate direct-I2C host API (see `z1010-cctv/CLAUDE.md` and
`ekfsm/devices/ekf_ccu_uc.py`) that bypasses this client entirely — don't confuse the two paths.
