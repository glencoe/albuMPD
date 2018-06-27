import unittest
from unittest.mock import create_autospec, call
import socket
import lib.MpdClient


class MpdClientTest(unittest.TestCase):

    def setup_socket_mocks(self, family=0, socket_type=0, proto=0, canonname=0, socket_address=0):
        """
        Returns a 5-tuple (family, type, proto, canonname, sockaddr)
        """

        socket_api = create_autospec(socket)
        socket_api.getaddrinfo.return_value = [(family, socket_type, proto, canonname, socket_address)]
        socket_object = create_autospec(socket.socket, instance=True)
        socket_api.socket.return_value = socket_object

        return socket_api, socket_object

    def test_connect(self):
        socket_api, socket_object = self.setup_socket_mocks()
        welcome_message = "OK MPD 0.20.0".encode()
        socket_object.recv.side_effect = [welcome_message]

        client = lib.MpdClient.MpdClient(socket_api)
        ok = client.connect("hal", 6600)

        self.assertEqual(
            [
                call.getaddrinfo('hal', 6600, socket_api.AF_UNSPEC, socket_api.SOCK_STREAM),
                call.socket(0, 0, 0),
            ],
            socket_api.method_calls)

        self.assertEqual(
            [
                call.connect(0),
                call.recv(len(welcome_message))
            ],
            socket_object.method_calls
        )

        self.assertEqual(ok, "Ok")

