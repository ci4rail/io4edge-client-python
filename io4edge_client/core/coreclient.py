from .protobufcom import PbCoreClient




def new_core_client(addr: str, command_timeout=5) -> PbCoreClient:
    """
    Create a new io4edge core client using protobuf communication.
    @param addr: address of io4edge function block (mdns name or "ip:port" address)
    @param command_timeout: timeout for commands in seconds
    @return: instance of PbCoreClient
    """
    # prepared to return later either a PbCoreClient or HTTPS REST API client
    return PbCoreClient(addr, command_timeout)
