import sys


class MpdClient:

    def __init__(self, socket_api):
        self._socket_api = socket_api
        self._socket = None

    def connect(self, host, port):
        for remote_socket in self._get_remote_socket_descriptions(host, port):
            af, socktype, proto, _, sa = remote_socket
            try:
                self._socket = self._create_matching_local_socket(af, socktype, proto)
            except OSError as msg:
                self._socket = None
                continue
            try:
                self._socket.connect(sa)
            except OSError as msg:
                self._socket.close()
                self._socket = None
                continue
            break
        if self._socket is None:
            print('could not open socket')
            sys.exit(1)
        elif self._received_welcome_message():
            return "Ok"

    def _received_welcome_message(self):
        welcome_message = "OK MPD 0.20.0"
        received_message = self._socket.recv(len(welcome_message)).decode("utf-8")
        return welcome_message == received_message

    def _receive_response(self):
        end_of_transmission_reached = False
        data = ""
        times = 0
        while not end_of_transmission_reached:
            data += self._socket.recv(1024).decode("utf-8")
            times += 1
            if data[-4:] == "\nOK\n":
                end_of_transmission_reached = True
        return data

    def command(self, command):
        self._socket.send((command + "\n").encode())
        return self._receive_response()

    def _get_remote_socket_descriptions(self, host, port):
        """
        Returns a 5-tuple (family, type, proto, canonname, sockaddr)
        """
        return self._socket_api.getaddrinfo(host, port,
                                            self._socket_api.AF_UNSPEC,
                                            self._socket_api.SOCK_STREAM)

    def _create_matching_local_socket(self, af, socktype, proto):
        return self._socket_api.socket(af, socktype, proto)
