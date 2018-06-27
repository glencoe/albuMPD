import lib.TcpFileView
import unittest
import socket
import io
from unittest.mock import MagicMock, create_autospec, call, sentinel


class TcpFileViewTest(unittest.TestCase):

    def setup_socket_mocks(self, family=0, socket_type=0, proto=0, canonname=0, socket_address=0):
        self._socket_api = create_autospec(socket)
        self._socket_api.getaddrinfo.return_value = [(family, socket_type, proto, canonname, socket_address)]
        self._socket_object = create_autospec(socket.socket, instance=True)
        self._socket_api.socket.return_value = self._socket_object
        self._write_file_handler = create_autospec(io.TextIOBase)
        self._read_file_handler = create_autospec(io.TextIOBase)
        self._socket_object.makefile.side_effect = self.makefile_mock

    def setUp(self):
        self.setup_socket_mocks(sentinel.family,
                                sentinel.socket_type,
                                sentinel.proto,
                                sentinel.canonname,
                                sentinel.socket_address)
        self.file_view = lib.TcpFileView.TcpFileView(self._socket_api)
        self.file_view.connect("hal", 6600)

    def test_connect(self):
        self.assertEqual(
            [
                call.getaddrinfo('hal', 6600, self._socket_api.AF_UNSPEC, self._socket_api.SOCK_STREAM),
                call.socket(sentinel.family, sentinel.socket_type, sentinel.proto),
            ],
            self._socket_api.method_calls)

        self.assertEqual(
            [
                call.connect(sentinel.socket_address),
                call.makefile(mode='r', encoding='utf-8'),
                call.makefile(mode='w', encoding='utf-8'),
            ],
            self._socket_object.method_calls
        )

    def test_write(self):
        self.file_view.write(sentinel.input_string)
        self.assertEqual(
            [
                call.write(sentinel.input_string),
                call.flush(),
            ],
            self._write_file_handler.method_calls
        )

    def test_read(self):
        self._read_file_handler.readline.return_value = sentinel.output_string
        output_string = self.file_view.read()
        self.assertEqual(sentinel.output_string, output_string)

    def makefile_mock(self, mode='r', encoding='utf-8'):
        if mode is 'r':
            return self._read_file_handler
        elif mode is 'w':
            return self._write_file_handler
        else:
            return None

