# SPDX-License-Identifier: Apache-2.0
import base64
from io import BytesIO
import json
from pathlib import Path
import tarfile
import tempfile
import unittest
from unittest.mock import patch

from io4edge_client.core import CoreClient, FirmwareAlreadyPresentError
from io4edge_client.core.coreclient import CoreClient as CoreClientBase
from io4edge_client.core.restcom import HttpsCoreClient, ParameterIsReadProtectedError


class TestCoreFactory(unittest.TestCase):
    def test_returns_core_client(self):
        self.assertIsInstance(
            CoreClient('localhost:443', connect=False), CoreClientBase)
        self.assertIsInstance(
            CoreClient('localhost:9999', connect=False), CoreClientBase)

    def test_transport_selection(self):
        with patch('io4edge_client.core.coreclient.PbCoreClient') as protobuf:
            for port in (443, 1443, 8443):
                self.assertIsInstance(CoreClient(f'localhost:{port}', connect=False),
                                      HttpsCoreClient)
            CoreClient('localhost:9999', 3, False)
            protobuf.assert_called_once_with('localhost:9999', 3, False)

    def test_mdns_selection(self):
        with patch('io4edge_client.core.coreclient.BaseClient._find_mdns',
                   return_value=('192.0.2.1', 1443)) as resolve:
            client = CoreClient('device', password='secret')
            self.assertIsInstance(client, HttpsCoreClient)
            self.assertEqual(client._addr, '192.0.2.1:1443')
            resolve.assert_called_once_with('device._io4edge-core._tcp')
        with patch('io4edge_client.core.coreclient.BaseClient._find_mdns',
                   return_value=(None, 0)):
            with self.assertRaisesRegex(RuntimeError, 'service not found'):
                CoreClient('missing')


class TestHttpsCore(unittest.TestCase):
    def setUp(self):
        self.patcher = patch('io4edge_client.core.restcom.httpscoreclient.HTTPSConnection')
        self.connection_class = self.patcher.start()
        self.addCleanup(self.patcher.stop)
        self.connection = self.connection_class.return_value
        self.response = self.connection.getresponse.return_value
        self.response.status = 200
        self.response.read.return_value = b'{}'
        self.client = HttpsCoreClient('localhost:443', 7, password='secret')

    def test_identification_auth_timeout_and_cleanup(self):
        self.response.read.return_value = b'{"name":"app","version":"1.2"}'
        firmware = self.client.identify_firmware()
        self.assertEqual((firmware.title, firmware.version), ('app', '1.2'))
        args, kwargs = self.connection.request.call_args
        self.assertEqual(args, ('GET', '/api/v1/firmware'))
        self.assertEqual(kwargs['headers']['Authorization'], 'Basic ' +
                         base64.b64encode(b'io4edge:secret').decode())
        self.assertEqual(self.connection_class.call_args.kwargs['timeout'], 7)
        self.connection.close.assert_called_once()
        self.response.read.return_value = b'{"part_number":"IOU","major_version":2,"serial_number":"123"}'
        hardware = self.client.identify_hardware()
        self.assertEqual((hardware.root_article, hardware.major_version,
                          hardware.serial_number), ('IOU', 2, '123'))

    def test_parameter_paths_and_payload(self):
        for name, path in [('foo', '/parameter/foo'),
                           ('ns.foo.bar', '/ns/parameter/foo.bar'),
                           ('ns.a/b?', '/ns/parameter/a%2Fb%3F')]:
            self.response.read.return_value = b'{"reboot_required":true}'
            self.assertTrue(self.client.set_persistent_parameter(name, 'value'))
            args, kwargs = self.connection.request.call_args
            self.assertEqual(args, ('PUT', '/api/v1' + path))
            self.assertEqual(json.loads(kwargs['body']), {'value': 'value'})
        self.response.read.return_value = b'{"value":"result"}'
        self.assertEqual(self.client.get_persistent_parameter('foo'), 'result')

    def test_errors_close_connection(self):
        self.response.status = 403
        self.response.getheader.return_value = 'application/json; charset=utf-8'
        self.response.read.return_value = b'{"code":"protected","message":"denied"}'
        with self.assertRaisesRegex(ParameterIsReadProtectedError, '403.*protected:denied'):
            self.client.get_persistent_parameter('secret')
        self.connection.close.assert_called_once()
        self.response.status = 500
        self.response.read.return_value = b'not json'
        with self.assertRaisesRegex(RuntimeError, '500'):
            self.client.restart()

    def test_timeout_closes_connection(self):
        self.connection.request.side_effect = TimeoutError
        with self.assertRaises(TimeoutError):
            self.client.identify_firmware()
        self.connection.close.assert_called_once()

    def test_firmware_chunks(self):
        for size in (0, 1, 10 * 1024, 10 * 1024 + 1, 20 * 1024):
            with self.subTest(size=size):
                self.connection.request.reset_mock()
                self.connection_class.reset_mock()
                firmware = bytes(i % 256 for i in range(size))
                progress = []
                self.client.load_firmware(firmware, progress.append)
                calls = self.connection.request.call_args_list
                self.assertEqual(b''.join(c.kwargs['body'] for c in calls), firmware)
                for i, call in enumerate(calls):
                    last = str(i == len(calls) - 1).lower()
                    self.assertEqual(call.args, ('PUT',
                        f'/api/v1/firmware?offset={i * 10 * 1024}&last={last}'))
                self.assertEqual(self.connection_class.call_count, 1)
                self.assertEqual(progress[-1], 100)

    def test_firmware_retry(self):
        self.connection.request.side_effect = [TimeoutError(), None]
        self.client.load_firmware(b'abc')
        calls = self.connection.request.call_args_list
        self.assertEqual(calls[0], calls[1])
        self.connection.request.reset_mock(side_effect=True)
        self.connection.request.side_effect = TimeoutError
        with self.assertRaisesRegex(RuntimeError, 'chunk command failed'):
            self.client.load_firmware(b'abc')
        self.assertEqual(self.connection.request.call_count, 4)

    def test_other_operations(self):
        self.client.program_hardware_identification('IOU', 2, '123')
        self.assertEqual(json.loads(self.connection.request.call_args.kwargs['body']),
                         {'part_number': 'IOU', 'major_version': 2, 'serial_number': '123'})
        self.client.restart()
        self.assertEqual(self.connection.request.call_args.args, ('POST', '/api/v1/restart'))
        self.response.read.return_value = b'raw data'
        self.assertEqual(self.client.get_parameter_set('ns'), b'raw data')
        self.assertEqual(self.client.load_parameter_set('ns', b'upload'), b'raw data')
        self.assertEqual(self.connection.request.call_args.args, ('PUT', '/api/v1/ns/parameterset'))
        self.assertEqual(self.client.repl_command('help'), 'raw data')
        self.client.change_api_password('new')
        self.assertEqual(self.client._password, 'new')
        with self.assertRaises(NotImplementedError):
            self.client.get_reset_reason()


class TestFirmwarePackage(unittest.TestCase):
    @staticmethod
    def package(manifest=None, firmware=b'firmware'):
        if manifest is None:
            manifest = {
                'name': 'application',
                'version': '2.0.0',
                'file': 'firmware.bin',
                'compatibility': {'hw': 's101-iou', 'major_revs': [1, 2]},
            }
        result = BytesIO()
        with tarfile.open(fileobj=result, mode='w') as archive:
            for name, data in (
                ('./manifest.json', json.dumps(manifest).encode()),
                ('./firmware.bin', firmware),
            ):
                info = tarfile.TarInfo(name)
                info.size = len(data)
                archive.addfile(info, BytesIO(data))
        return result.getvalue()

    def setUp(self):
        self.client = HttpsCoreClient('localhost:443', connect=False)
        self.firmware_id = type('FirmwareId', (), {
            'title': 'fw-other', 'version': '1.0.0'})()
        self.hardware_id = type('HardwareId', (), {
            'root_article': 'S101-IOU01', 'major_version': 2})()

    def test_loads_package_from_bytes(self):
        with patch.object(self.client, 'identify_firmware',
                          return_value=self.firmware_id), \
             patch.object(self.client, 'identify_hardware',
                          return_value=self.hardware_id), \
             patch.object(self.client, 'load_firmware') as load:
            progress = object()
            self.client.load_firmware_package(
                self.package(firmware=b'binary'), progress)
            load.assert_called_once_with(b'binary', progress)

    def test_loads_package_from_file(self):
        with tempfile.TemporaryDirectory() as directory:
            package_path = Path(directory) / 'firmware.fwpkg'
            package_path.write_bytes(self.package(firmware=b'binary'))
            with patch.object(self.client, 'identify_firmware',
                              return_value=self.firmware_id), \
                 patch.object(self.client, 'identify_hardware',
                              return_value=self.hardware_id), \
                 patch.object(self.client, 'load_firmware') as load:
                self.client.load_firmware_package(package_path)
                load.assert_called_once_with(b'binary', None)

    def test_rejects_incompatible_hardware(self):
        self.hardware_id.root_article = 'S102-IOU01'
        with patch.object(self.client, 'identify_firmware',
                          return_value=self.firmware_id), \
             patch.object(self.client, 'identify_hardware',
                          return_value=self.hardware_id), \
             patch.object(self.client, 'load_firmware') as load:
            with self.assertRaisesRegex(ValueError, 'not suitable'):
                self.client.load_firmware_package(self.package())
            load.assert_not_called()

        self.hardware_id.root_article = 'S101-IOU01'
        self.hardware_id.major_version = 3
        with patch.object(self.client, 'identify_firmware',
                          return_value=self.firmware_id), \
             patch.object(self.client, 'identify_hardware',
                          return_value=self.hardware_id):
            with self.assertRaisesRegex(ValueError, 'version 3'):
                self.client.load_firmware_package(self.package())

    def test_rejects_firmware_already_present(self):
        self.firmware_id.title = 'FW-APPLICATION'
        self.firmware_id.version = '2.0.0'
        with patch.object(self.client, 'identify_firmware',
                          return_value=self.firmware_id), \
             patch.object(self.client, 'identify_hardware',
                          return_value=self.hardware_id), \
             patch.object(self.client, 'load_firmware') as load:
            with self.assertRaises(FirmwareAlreadyPresentError):
                self.client.load_firmware_package(self.package())
            load.assert_not_called()

    def test_rejects_invalid_package(self):
        with self.assertRaisesRegex(ValueError, 'Cannot read firmware package'):
            self.client.load_firmware_package(b'not a tar')

        manifest = {
            'name': 'application', 'version': '2.0.0',
            'file': 'firmware.bin',
            'compatibility': {'hw': 's101-iou', 'major_revs': []},
        }
        with self.assertRaisesRegex(ValueError, 'major_revs'):
            self.client.load_firmware_package(self.package(manifest))


if __name__ == '__main__':
    unittest.main()
