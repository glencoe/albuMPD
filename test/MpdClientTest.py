import unittest
from unittest.mock import create_autospec, call
from lib.TcpFileView import TcpFileView
from lib.MpdClient import MpdClient

class MpdClientTest(unittest.TestCase):

    def setUp(self):
        self._file_view = create_autospec(TcpFileView)
        self._client = MpdClient(self._file_view)

