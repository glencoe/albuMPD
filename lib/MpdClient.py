import lib.ResponseParser


class MpdClientError(BaseException):
    pass


class MpdClient:

    def __init__(self, file_view, parse_response=lib.ResponseParser.parse_response, logger=None):
        self._file_view = file_view
        self._parse_response = parse_response
        self._logger = logger

    def connect(self, host, port):
        self._file_view.connect(host, port)
        welcome_message = self._file_view.read()
        if not welcome_message.startswith("OK MPD "):
            raise MpdClientError("Error: received invalid welcome message:\n  " + welcome_message)

    def list(self, what, group_tags=None, filter=None):
        request_list = ["list", what]
        if filter is not None:
            request_list += filter
        if group_tags is not None:
            group_tags = [x for t in group_tags for x in ("group", t)]
            request_list += group_tags
        return self.request(*request_list)

    @staticmethod
    def _quote_special_chars(string):
        if ' ' in string or '\\\"' in string:
            return '"{}"'.format(string)
        else:
            return string

    def request(self, command, *args):
        self._send_request(command, *args)
        return self._read()

    def _send_request(self, command, *args):
        if args is not None and len(args) > 0:
            args = [self._quote_special_chars(str(x).replace('"', '\\\"')) for x in args]
            arg_string = " ".join(args)
            request = '{} {}\n'.format(command, arg_string)
        else:
            request = '{}\n'.format(command)
        self._file_view.write(request)

    def stats(self):
        return self.request("stats")

    def status(self):
        return self.request("status")

    def find(self, *what):
        return self.request('find', *what)

    def _read(self):
        return self._parse_response(self._get_response_utf8())

    def _album_art_chunk(self, uri, offset=0):
        self._send_request('albumart', uri, '{}'.format(offset))
        byte_string = b''
        while byte_string.count(b'\n') < 2 and byte_string != b'ACK':
            byte_string += self._file_view.read_bytes(1)
        if byte_string == b'ACK':
            end_of_transmission_reached = False
            while not end_of_transmission_reached:
                current_byte = self._file_view.read_bytes(1)
                if current_byte is b'\n':
                    end_of_transmission_reached = True
                else:
                    byte_string += current_byte
            raise MpdClientError(byte_string.decode())
        size, _, rest = byte_string.partition('\n'.encode())
        size = size.decode().split(":")[-1].lstrip()
        size = int(size)
        number_of_bytes, _, rest = rest.partition('\n'.encode())
        number_of_bytes = number_of_bytes.decode().split(":")[-1].lstrip()
        number_of_bytes = int(number_of_bytes)
        rest += self._file_view.read_bytes(number_of_bytes)
        self._file_view.read_bytes(4)
        next_offset = number_of_bytes + offset
        complete = offset + number_of_bytes >= size
        self._log("{}/{}/{}/{}\n".format(offset, size, next_offset, complete))
        return rest, next_offset, complete

    def album_art(self, uri):
        complete = False
        data = b''
        offset = 0
        while not complete:
            chunk, offset, complete = self._album_art_chunk(uri, offset)
            data += chunk
        return data

    def _get_response_utf8(self):
        response = ""
        end_of_transmission = False
        while not end_of_transmission:
            line = self._file_view.read()
            if line.startswith("OK"):
                end_of_transmission = True
            elif line.startswith("ACK"):
                raise MpdClientError(line)
            else:
                response += line
        return response

    def _read_number_of_lines(self, number):
        response = ""
        i = 0
        while i < number:
            response += self._file_view.read()
            i += 1
        return self._parse_response(response)

    def shutdown(self):
        self._file_view.close()

    def _log(self, string):
        if self._logger is not None:
            self._logger.write(string)
