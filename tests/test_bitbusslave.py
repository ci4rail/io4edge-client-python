# SPDX-License-Identifier: Apache-2.0
import unittest
from unittest.mock import patch

from io4edge_client.bitbusslave import Client, Pb


class TestBitbusSlaveClient(unittest.TestCase):
    @patch("io4edge_client.bitbusslave.client.FbClient")
    def test_set_tx_message(self, fb_client_type):
        client = Client("192.168.1.100:9999", connect=False)

        client.set_tx_message(b"response")

        fb_client = fb_client_type.return_value
        command = fb_client.function_control_set.call_args.args[0]
        self.assertEqual(command.tx_msg.bitbus_information, b"response")

    @patch("io4edge_client.bitbusslave.client.FbClient")
    def test_get_state(self, fb_client_type):
        client = Client("192.168.1.100:9999", connect=False)
        fb_client = fb_client_type.return_value

        state = client.get_state()

        self.assertIsInstance(state, Pb.FunctionControlGetResponse)
        fb_client.function_control_get.assert_called_once()

    @patch("io4edge_client.bitbusslave.client.FbClient")
    def test_stream_factories(self, fb_client_type):
        client = Client("192.168.1.100:9999", connect=False)

        self.assertIsInstance(client._create_stream_data(), Pb.StreamData)
        self.assertIsInstance(
            client._create_default_stream_config(), Pb.StreamControlStart
        )
        fb_client_type.assert_called_once_with(
            "_io4edge_bitbusSlave._tcp", "192.168.1.100:9999", 5, connect=False
        )


if __name__ == "__main__":
    unittest.main()
