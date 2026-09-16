# SPDX-License-Identifier: Apache-2.0
import unittest
from unittest.mock import patch

from io4edge_client.bitbussniffer import Client, Pb


class TestBitbusSnifferClient(unittest.TestCase):
    @patch("io4edge_client.bitbussniffer.client.FbClient")
    def test_send_frame(self, fb_client_type):
        client = Client("192.168.1.100:9999", connect=False)

        client.send_frame(b"frame")

        command = fb_client_type.return_value.function_control_set.call_args.args[0]
        self.assertEqual(command.bitbus_frame, b"frame")
        self.assertIsInstance(
            fb_client_type.return_value.function_control_set.call_args.args[1],
            Pb.FunctionControlSetResponse,
        )


if __name__ == "__main__":
    unittest.main()
