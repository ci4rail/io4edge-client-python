# SPDX-License-Identifier: Apache-2.0

from pathlib import Path
import re
import subprocess

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
from .eeprom import Client as EepromClient
from .mvbsniffer import Client as MvbSnifferClient
from .pixelDisplay import Client as PixelDisplayClient
from .ssm import Client as SsmClient
# from .watchdog import Client as WatchdogClient

# Import core clients
from .core import CoreClient
from .functionblock import Client as FunctionblockClient

# This create _version.py file if it doesn't exist,
# using git describe to generate version information
# Use when running from source, but will be ignored when installed via pip (since _version.py is in .gitignore)
def _version_tuple_from_git() -> tuple:
    package_dir = Path(__file__).resolve().parent
    repo_dir = package_dir.parent

    try:
        describe = subprocess.run(
            ["git", "describe", "--tags", "--long", "--dirty", "--always"],
            cwd=repo_dir,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return (0, 0, 0, "dev0")

    match = re.match(r"^v?(\d+)\.(\d+)\.(\d+)-(\d+)-g[0-9a-f]+(?:-dirty)?$", describe)
    if not match:
        return (0, 0, 0, "dev0")

    major, minor, patch, distance = (int(part) for part in match.groups())
    if distance == 0 and not describe.endswith("-dirty"):
        return (major, minor, patch)

    return (major, minor, patch + 1, f"dev{distance}")


def _ensure_version_file() -> None:
    version_path = Path(__file__).resolve().with_name("_version.py")
    if version_path.exists():
        return

    generated_version = _version_tuple_from_git()
    version_path.write_text(
        "# SPDX-License-Identifier: Apache-2.0\n"
        f"version = {generated_version!r}\n"
        'VERSION = ".".join(str(x) for x in version)\n',
        encoding="utf-8",
    )


# Version information
_ensure_version_file()
from ._version import version, VERSION

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
    "EepromClient",
    "MvbSnifferClient",
    "PixelDisplayClient",
    "SsmClient",

    # Core clients
    "CoreClient",
    "FunctionblockClient",

    # Version
    "version",
    "VERSION"
]
