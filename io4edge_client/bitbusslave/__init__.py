# SPDX-License-Identifier: Apache-2.0

from .client import Client
import io4edge_client.api.bitbusSlave.python.bitbusSlave.v1.bitbusSlave_pb2 as Pb

__all__ = ["Client", "Pb"]
