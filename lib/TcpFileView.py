import sys


class TcpFileView:

    def __init__(self, socket_api):
        self._port = 0
        self._host = ""
        self._socket = None
        self._socket_api = socket_api
        self._write_file_handle = None
        self._read_file_handle = None

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
                self._read_file_handle.close()
                self._write_file_handle.close()
                self._socket = None
                continue
            break
        if self._socket is None:
            print('could not open socket')
        else:
            self._read_file_handle = self._socket.makefile(mode='r', encoding='utf-8')
            self._write_file_handle = self._socket.makefile(mode='w', encoding='utf-8')

    def reconnect(self):
        self.connect(self._host, self._port)

    def is_closed(self):
        return self._socket is None

    def _get_remote_socket_descriptions(self, host, port):
        """
        Returns a 5-tuple (family, type, proto, canonname, sockaddr)
        """
        return self._socket_api.getaddrinfo(host, port,
                                            self._socket_api.AF_UNSPEC,
                                            self._socket_api.SOCK_STREAM)

    def _create_matching_local_socket(self, af, socktype, proto):
        return self._socket_api.socket(af, socktype, proto)

    def write(self, string):
        self._write_file_handle.write(string)
        self._write_file_handle.flush()

    def read(self):
        return self._read_file_handle.readline()
