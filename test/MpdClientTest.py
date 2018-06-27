import unittest
from unittest.mock import create_autospec, call
import socket
import lib.MpdClient


class MpdClientTest(unittest.TestCase):

    def setup_socket_mocks(self, family=0, socket_type=0, proto=0, canonname=0, socket_address=0):
        socket_api = create_autospec(socket)
        socket_api.getaddrinfo.return_value = [(family, socket_type, proto, canonname, socket_address)]
        socket_object = create_autospec(socket.socket, instance=True)
        socket_api.socket.return_value = socket_object

        return socket_api, socket_object

    def test_connect(self):
        socket_api, socket_object = self.setup_socket_mocks()

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
            ],
            socket_object.method_calls
        )


    def test_send_command(self):
        socket_api, socket_object = self.setup_socket_mocks()
        string_partition = ["""AlbumArtist: Yes
Album: The Yes Album
AlbumArtist: Yes
Album: Time and a Word
AlbumArtist: Yes
""", """Album: Yes
AlbumArtist: Yo La Tengo
Album: I Can Hear the Heart Beating as One
AlbumArtist: Young Magic
Album: Melt
AlbumArtist: Young Rascals
Album: Special Edition  (Good Lovin')
OK
"""]
        string_joined = "".join(string_partition)
        welcome_message = "OK MPD 0.20.0"
        socket_object.recv.side_effect = [welcome_message.encode()] + [x.encode() for x in string_partition]
        client = lib.MpdClient.MpdClient(socket_api)
        client.connect("host", 1000)
        result = client.command("list albumartist group album")
        self.assertEqual(
            [
                call.send("list albumartist group album\n".encode()),
                call.recv(1024),
                call.recv(1024)
            ],
            socket_object.method_calls[-3:]
        )
        self.assertEqual(result, string_joined)

