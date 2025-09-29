# io4edge-client-python Copilot Instructions

## Architecture Overview

This Python SDK provides client libraries for io4edge devices - intelligent I/O devices connected via network. The codebase follows a layered architecture:

- **Base Layer** (`io4edge_client/base/`): Core networking with mDNS service discovery and socket transport
- **Functionblock Layer** (`io4edge_client/functionblock/`): Generic function block client with command/stream handling
- **Device-Specific Clients**: Type-specific implementations (analogintypea, binaryiotypea, etc.)
- **Generated APIs** (`io4edge_client/api/`): Protobuf definitions and generated Python code

## Key Patterns & Conventions

### Client Architecture Pattern
All device clients follow this consistent pattern:
```python
class Client:
    def __init__(self, addr: str, command_timeout=5):
        self._fb_client = FbClient("_io4edge_<device_type>._tcp", addr, command_timeout)
```

Each client wraps a `functionblock.Client` instance and provides device-specific methods. See `analogintypea/client.py` as the canonical example.

### Service Naming Convention
- mDNS services: `_io4edge_<functionblock>._tcp` (e.g., `_io4edge_analogInTypeA._tcp`)
- Address format: either mDNS name (e.g., "S101-IOU01-USB-EXT-1") or IP:port ("192.168.1.100:9999")

### Configuration & Control Methods
Standard methods across all clients:
- `upload_configuration(config)` / `download_configuration()` - Device configuration
- `function_control_set()` / `function_control_get()` - Runtime control/status
- `start_stream()` / `stop_stream()` / `read_stream()` - Data streaming
- `close()` - Cleanup and thread termination

### Protobuf Integration
- Import protobuf modules as `Pb` alias: `import ...analogInTypeA_pb2 as Pb`
- Use `google.protobuf.any_pb2.Any` for generic message wrapping
- Protobuf files generated from `io4edge_client/api/` subdirectory

## Development Workflows

### Adding New Device Support
1. Create new module directory under `io4edge_client/`
2. Implement `Client` class following the established pattern
3. Import device-specific protobuf as `Pb`
4. Add example usage in `examples/<device_type>/`
5. Ensure service name follows `_io4edge_<type>._tcp` convention

### Stream Handling Pattern
Streaming uses producer-consumer pattern with background thread:
```python
# Producer thread reads socket, queues messages
# Consumer calls read_stream() with optional timeout
generic_data, specific_data = client.read_stream(timeout=1.0)
```

### Testing
- Unit tests in `tests/` focus on parsing and address handling
- Integration examples in `examples/` serve as functional tests
- Use `python -m unittest` for running tests

## Critical Implementation Details

### Thread Safety
- `functionblock.Client` uses internal threading for stream handling
- Always call `close()` to properly terminate background threads
- Command/response uses mutex protection for single-command-at-a-time

### Error Handling
- Commands raise `RuntimeError` for protocol errors
- `TimeoutError` for command timeouts (default 5 seconds)
- Stream reads raise `TimeoutError` when no data available

### Address Resolution
Base client automatically handles:
- Direct IP:port addresses: `"192.168.1.100:9999"`
- mDNS service names: `"S101-IOU01-USB-EXT-1"` (automatically appends service type)

## Protobuf Code Generation

The `io4edge_client/api/` directory contains a git submodule with protobuf definitions. Use `make` in that directory to regenerate Python protobuf code when proto files change.

## Docker Deployment

For containerized deployment, use host networking mode to access mDNS services:
```bash
docker run --network=host <image> <script-args>
```

## Common Pitfalls

- Always use absolute imports for protobuf modules to avoid conflicts
- Call `client.close()` in cleanup/exception handlers to prevent thread leaks
- Check device-specific protobuf documentation for field constraints
- Service discovery requires network connectivity to device's mDNS announcements
