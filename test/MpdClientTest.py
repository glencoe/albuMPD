import unittest
from unittest.mock import create_autospec, call
from lib.TcpFileView import TcpFileView
from lib.MpdClient import MpdClient, MpdClientError


class MpdClientTest(unittest.TestCase):

    def setUp(self):
        self._file_view = create_autospec(TcpFileView)
        self._client = MpdClient(self._file_view)

    def test_failed_connect(self):
        self._file_view.read.return_value = "Some wrong welcome message"
        self.assertRaises(MpdClientError, self._client.connect, "hal", 6600)

    def test_failed_command(self):
        self._client.connect("host", 0)
        self._file_view.read.return_value = "ACK [5@0] {} unknown command 'unknown_command'"
        self.assertRaises(MpdClientError, self._client.list, "album")

