from abc import ABC, abstractmethod
from io import BytesIO
import json
from os import PathLike
import tarfile
from typing import Callable

from io4edge_client.base import Client as BaseClient
from .types import FirmwareIdentification, HardwareIdentification


class FirmwareAlreadyPresentError(RuntimeError):
    """The firmware contained in a package is already running."""


class CoreClient(ABC):
    """Behavior shared by the protobuf and HTTPS core clients."""

    @abstractmethod
    def identify_firmware(self) -> FirmwareIdentification:
        """Return the firmware currently running on the device."""
        raise NotImplementedError

    @abstractmethod
    def identify_hardware(self) -> HardwareIdentification:
        """Return the device hardware identification."""
        raise NotImplementedError

    @abstractmethod
    def load_firmware(
        self,
        firmware: bytes,
        progress_cb: Callable[[float], None] | None = None,
    ) -> None:
        """Upload a raw firmware binary to the device."""
        raise NotImplementedError

    def load_firmware_package(
        self,
        package: str | PathLike[str] | bytes,
        progress_cb: Callable[[float], None] | None = None,
    ) -> None:
        """Validate and load an io4edge ``.fwpkg`` firmware package.

        ``package`` may be a filesystem path or the package contents. Before
        uploading, the manifest is checked against the device hardware and
        currently running firmware. The packaged binary is passed to the
        transport-specific :meth:`load_firmware` implementation.
        """
        try:
            if isinstance(package, bytes):
                archive_context = tarfile.open(
                    fileobj=BytesIO(package), mode="r:")
            else:
                archive_context = tarfile.open(package, mode="r:")
            with archive_context as archive:
                manifest_data = self._read_package_member(
                    archive, "manifest.json")
                try:
                    manifest = json.loads(manifest_data)
                except (UnicodeDecodeError, json.JSONDecodeError) as error:
                    raise ValueError("Cannot decode firmware manifest") from error

                name = self._manifest_value(manifest, "name", str)
                version = self._manifest_value(manifest, "version", str)
                filename = self._manifest_value(manifest, "file", str)
                compatibility = self._manifest_value(
                    manifest, "compatibility", dict)
                hardware_name = self._manifest_value(
                    compatibility, "hw", str, "compatibility.hw")
                major_revisions = self._manifest_value(
                    compatibility, "major_revs", list,
                    "compatibility.major_revs")
                if not major_revisions or any(
                    type(revision) is not int for revision in major_revisions
                ):
                    raise ValueError(
                        'Invalid "compatibility.major_revs" in manifest')

                firmware = self._read_package_member(archive, filename)
        except (tarfile.TarError, OSError) as error:
            raise ValueError("Cannot read firmware package") from error

        installed = self.identify_firmware()
        hardware = self.identify_hardware()
        self._assert_firmware_compatible(
            hardware_name, major_revisions, hardware.root_article,
            hardware.major_version)

        package_name = name if name.startswith("fw-") else "fw-" + name
        if (installed.title.casefold() == package_name.casefold()
                and installed.version == version):
            raise FirmwareAlreadyPresentError(
                "Requested firmware is already present")

        self.load_firmware(firmware, progress_cb)

    @staticmethod
    def _manifest_value(manifest, key, expected_type, path=None):
        value = manifest.get(key) if isinstance(manifest, dict) else None
        if not value or type(value) is not expected_type:
            raise ValueError(f'Missing or invalid "{path or key}" in manifest')
        return value

    @staticmethod
    def _read_package_member(archive: tarfile.TarFile, filename: str) -> bytes:
        wanted = filename.removeprefix("./")
        member = next(
            (item for item in archive.getmembers()
             if item.isfile() and item.name.removeprefix("./") == wanted),
            None,
        )
        if member is None:
            raise ValueError(f'File "{filename}" missing from firmware package')
        extracted = archive.extractfile(member)
        if extracted is None:
            raise ValueError(f'Cannot read "{filename}" from firmware package')
        return extracted.read()

    @staticmethod
    def _assert_firmware_compatible(
        firmware_hardware: str,
        firmware_major_revisions: list[int],
        device_hardware: str,
        device_major_revision: int,
    ) -> None:
        prefix = device_hardware[:len(firmware_hardware)]
        if (len(firmware_hardware) > len(device_hardware)
                or firmware_hardware.casefold() != prefix.casefold()):
            raise ValueError(
                f"Firmware {firmware_hardware} is not suitable for hardware "
                f"{device_hardware}")
        if device_major_revision not in firmware_major_revisions:
            raise ValueError(
                "Firmware does not support hardware version "
                f"{device_major_revision}")


# Imported after CoreClient is defined because transport implementations inherit
# its package-loading behavior.
from .protobufcom import PbCoreClient  # noqa: E402
from .restcom import HttpsCoreClient  # noqa: E402


def new_core_client(addr: str, command_timeout=5, connect=True,
                    password="") -> CoreClient:
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
