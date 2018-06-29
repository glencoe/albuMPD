class TcpFileViewError(BaseException):
    pass


class TcpFileView:

    def __init__(self, socket_api):
        self._port = 0
        self._host = ""
        self._socket = None
        self._socket_api = socket_api
        self._write_file_handle = None
        self._read_file_handle = None

    def connect(self, host=None, port=None):
        if host is None or port is None:
            self._do_reconnect()
        else:
            self._do_connect(host, port)

    def _do_connect(self, host, port):
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
                self._socket.shutdown(self._socket_api.SHUT_RDWR)
                self._socket.close()
                self._socket = None
                continue
            break
        if self._socket is None:
            raise TcpFileViewError
        else:
            self._read_file_handle = self._socket.makefile(mode='r', encoding='utf-8')
            self._write_file_handle = self._socket.makefile(mode='w', encoding='utf-8')
            self._read_binary_handle = self._socket.makefile(mode='b')

    def _do_reconnect(self):
        self._do_connect(self._host, self._port)

    def is_closed(self):
        return self._socket is None

    def close(self):
        self._close_socket()
        self._close_read_file_handle()
        self._close_write_file_handle()
        self._close_read_binary_handle()

    def _close_socket(self):
        if self._socket is not None:
            self._socket.shutdown(self._socket_api.SHUT_RDWR)
            self._socket.close()
            self._socket = None

    def _close_read_file_handle(self):
        if self._read_file_handle is not None:
            self._read_file_handle.close()
            self._read_file_handle = None

    def _close_write_file_handle(self):
        if self._write_file_handle is not None:
            self._write_file_handle.close()
            self._write_file_handle = None

    def _close_read_binary_handle(self):
        if self._read_binary_handle is not None:
            self._read_binary_handle.close()
            self._read_binary_handle = None

    def _get_remote_socket_descriptions(self, host, port):
        """
        Returns a 5-tuple (family, type, proto, canonname, sockaddr)
        """
        return self._socket_api.getaddrinfo(host, port,
                                            self._socket_api.AF_UNSPEC,
                                            self._socket_api.SOCK_STREAM)

    def _create_matching_local_socket(self, af, socket_type, proto):
        return self._socket_api.socket(af, socket_type, proto)

    def write(self, string):
        self._try_call(self._write_file_handle.write, string)
        self._try_call(self._write_file_handle.flush)

    def read(self):
        return self._try_call(self._read_file_handle.readline)

    def _try_call(self, call, *args):
        try:
            if args is None or len(args) == 0:
                result = call()
            else:
                result = call(*args)
        except OSError as msg:
            self.close()
            raise TcpFileViewError
        if result is "":
            self.close()
            raise TcpFileViewError
        return result

    def read_bytes(self, number):
        return self._try_call(self._read_binary_handle.read, number)
