from io4edge_client.base import Client as BaseClient
from .protobufcom import PbCoreClient
from .restcom import HttpsCoreClient


def new_core_client(addr: str, command_timeout=5, connect=True,
                    password="") -> PbCoreClient | HttpsCoreClient:
    """Create a core client for an mDNS name or ``host:port`` address.

    Ports whose remainder modulo 1000 is 443 use HTTPS, all others protobuf/TCP.
    ``command_timeout`` is in seconds. ``password`` is used only for HTTPS
    Basic authentication as user ``io4edge`` (default: empty password).
    """
    try:
        ip, port = BaseClient._net_address_split(addr)
    except ValueError:
        ip, port = BaseClient._find_mdns(addr + "._io4edge-core._tcp")
    if ip is None:
        raise RuntimeError("service not found")
    resolved_addr = f"{ip}:{port}"
    if port % 1000 == 443:
        return HttpsCoreClient(resolved_addr, command_timeout, connect, password)
    return PbCoreClient(resolved_addr, command_timeout, connect)
