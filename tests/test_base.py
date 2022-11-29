# SPDX-License-Identifer: Apache-2.0
import unittest
import io4edge_client.base as base


class TestBase(unittest.TestCase):
    def test_net_address_split_ok(self):
        ip, port = base.Client._net_address_split("192.168.200.1:9999")
        self.assertEqual(ip, "192.168.200.1")
        self.assertEqual(port, 9999)

    def test_net_address_split_nok(self):
        with self.assertRaises(ValueError):
            ip, port = base.Client._net_address_split("abc")

    def test_split_service_ok(self):
        instance, service = base.Client._split_service(
            "iou04-usb-ext-4._io4edge-core._tcp"
        )
        self.assertEqual(instance, "iou04-usb-ext-4")
        self.assertEqual(service, "_io4edge-core._tcp")

        instance, service = base.Client._split_service("foo.bar.baz._io4edge-core._tcp")
        self.assertEqual(instance, "foo.bar.baz")
        self.assertEqual(service, "_io4edge-core._tcp")

    def test_split_service_nok(self):
        with self.assertRaises(ValueError):
            _, _ = base.Client._net_address_split("_io4edge-core._tcp")


if __name__ == "__main__":
    unittest.main()
