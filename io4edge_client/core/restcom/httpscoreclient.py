# SPDX-License-Identifier: Apache-2.0
"""HTTPS implementation of the io4edge core REST API."""
import base64
from http.client import HTTPSConnection
import json
import ssl
from typing import Callable
from urllib.parse import quote, urlencode

from ..types import FirmwareIdentification, HardwareIdentification


class ParameterIsReadProtectedError(RuntimeError):
    """The device forbids reading a persistent parameter."""


class HttpsCoreClient:
    """Core REST client using Basic authentication with user ``io4edge``.

    Like the Go client, accepts self-signed device certificates. Connections
    are opened per request; ``connect`` is accepted for factory compatibility.
    Command timeouts apply to socket operations, including firmware chunks.
    """

    def __init__(self, addr: str, command_timeout=5, connect=True, password=""):
        self._addr = addr
        self._command_timeout = command_timeout
        self._password = password
        self._context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        self._context.check_hostname = False
        self._context.verify_mode = ssl.CERT_NONE

    def open(self) -> None:
        """No persistent connection is required for REST requests."""

    def close(self) -> None:
        """Requests close their own connections."""

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def _request(self, path, method="GET", body=None, params=None,
                 read_parameter=False):
        credentials = base64.b64encode(
            f"io4edge:{self._password}".encode()).decode("ascii")
        headers = {"Authorization": f"Basic {credentials}"}
        if isinstance(body, dict):
            body = json.dumps(body).encode()
            headers["Content-Type"] = "application/json"
        elif body is not None:
            headers["Content-Type"] = "application/octet-stream"
        path = "/api/v1" + path
        if params is not None:
            path += "?" + urlencode(params)
        connection = HTTPSConnection(
            self._addr, timeout=self._command_timeout, context=self._context)
        try:
            connection.request(method, path, body=body, headers=headers)
            response = connection.getresponse()
            data = response.read()
            if response.status != 200:
                detail = ""
                if response.getheader("Content-Type", "").split(";")[0] == "application/json":
                    try:
                        error = json.loads(data)
                        detail = f" ({error['code']}:{error['message']})"
                    except (ValueError, KeyError, TypeError):
                        pass
                error_type = (ParameterIsReadProtectedError
                              if read_parameter and response.status == 403
                              else RuntimeError)
                raise error_type(f"Unexpected status code {response.status}{detail}")
            return data
        finally:
            connection.close()

    def identify_hardware(self) -> HardwareIdentification:
        data = json.loads(self._request("/hardware"))
        for name, expected in (("part_number", str), ("serial_number", str),
                               ("major_version", int)):
            if type(data.get(name)) is not expected:
                raise RuntimeError(f"Missing or invalid hardware field: {name}")
        return HardwareIdentification(data["part_number"], data["major_version"],
                                      data["serial_number"])

    def program_hardware_identification(
        self, root_article: str, major_version: int, serial_number: str
    ) -> None:
        self._request("/hardware", "PUT", {
            "part_number": root_article, "major_version": major_version,
            "serial_number": serial_number})

    def identify_firmware(self) -> FirmwareIdentification:
        data = json.loads(self._request("/firmware"))
        return FirmwareIdentification(data["name"], data["version"])

    def load_firmware(self, firmware: bytes,
                      progress_cb: Callable[[float], None] | None = None) -> None:
        """Upload raw firmware in 1024-byte chunks, retrying failures three times.

        The device restarts after the final chunk. Progress is a percentage.
        """
        total = len(firmware)
        for offset in range(0, max(total, 1), 1024):
            chunk = firmware[offset:offset + 1024]
            end = offset + len(chunk)
            for attempt in range(4):
                try:
                    self._request("/firmware", "PUT", chunk,
                                  {"offset": offset, "last": str(end == total).lower()})
                    break
                except (OSError, RuntimeError) as error:
                    if attempt == 3:
                        raise RuntimeError("Load firmware chunk command failed") from error
            if progress_cb:
                progress_cb(end / total * 100 if total else 100)

    def restart(self) -> None:
        self._request("/restart", "POST")

    @staticmethod
    def _parameter_path(name):
        namespace, separator, parameter = name.partition(".")
        if not separator:
            parameter, namespace = namespace, ""
        prefix = "/" + quote(namespace, safe="") if namespace else ""
        return prefix + "/parameter/" + quote(parameter, safe="")

    def set_persistent_parameter(self, name: str, value: str) -> bool:
        """Set a parameter and return whether a reboot is required."""
        data = self._request(self._parameter_path(name), "PUT", {"value": value})
        return json.loads(data).get("reboot_required", False)

    def get_persistent_parameter(self, name: str) -> str:
        data = self._request(self._parameter_path(name), read_parameter=True)
        return json.loads(data)["value"]

    def get_parameter_set(self, namespace: str) -> bytes:
        return self._request(f"/{quote(namespace, safe='')}/parameterset")

    def load_parameter_set(self, namespace: str, data: bytes) -> bytes:
        return self._request(f"/{quote(namespace, safe='')}/parameterset", "PUT", data)

    def change_api_password(self, new_password: str) -> None:
        self._request("/users/io4edge/basic_auth", "PUT", {"password": new_password})
        self._password = new_password

    def repl_command(self, cmd: str) -> str:
        return self._request("/repl", "POST", cmd.encode()).decode()

    def get_reset_reason(self) -> str:
        raise NotImplementedError("Reset reason is not implemented by the REST API")
