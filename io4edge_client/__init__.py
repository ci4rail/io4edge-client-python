# SPDX-License-Identifier: Apache-2.0

# Import all client classes with descriptive names
from .analogintypea import Client as AnalogInTypeAClient
from .analogintypeb import Client as AnalogInTypeBClient
from .binaryiotypea import Client as BinaryIoTypeAClient
from .binaryiotypeb import Client as BinaryIoTypeBClient
from .binaryiotypec import Client as BinaryIoTypeCClient
from .binaryiotyped import Client as BinaryIoTypeDClient
from .bitbussniffer import Client as BitbusSnifferClient
from .canl2 import Client as CanL2Client
from .colorLED import Client as ColorLEDClient
from .digiwave import Client as DigiwaveClient
from .mvbsniffer import Client as MvbSnifferClient
from .pixelDisplay import Client as PixelDisplayClient
from .watchdog import Client as WatchdogClient

# Import core clients
from .core import CoreClient
from .functionblock import Client as FunctionblockClient

# Version information
from .version import __version__

__all__ = [
    # Device-specific clients
    "AnalogInTypeAClient",
    "AnalogInTypeBClient",
    "BinaryIoTypeAClient",
    "BinaryIoTypeBClient",
    "BinaryIoTypeCClient",
    "BinaryIoTypeDClient",
    "BitbusSnifferClient",
    "CanL2Client",
    "ColorLEDClient",
    "DigiwaveClient",
    "MvbSnifferClient",
    "PixelDisplayClient",
    "WatchdogClient",

    # Core clients
    "CoreClient",
    "FunctionblockClient",

    # Version
    "__version__"
]
