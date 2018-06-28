import lib.ResponseParser


class MpdClientError(BaseException):
    pass


class MpdClient:

    def __init__(self, file_view, parse_response=lib.ResponseParser.parse_response):
        self._file_view = file_view
        self._parse_response = parse_response

    def connect(self, host, port):
        self._file_view.connect(host, port)
        welcome_message = self._file_view.read()
        if not welcome_message.startswith("OK MPD "):
            raise MpdClientError("Error: received invalid welcome message:\n  " + welcome_message)

    def list(self, what, group_tags=None, filter=None):
        request = "list " + what
        if filter is not None:
            request += " " + filter
        if group_tags is not None:
            for tag in group_tags:
                request += " group " + tag
        return self.command(request)

    def command(self, request):
        print(request)
        request = "{}\n".format(request)
        self._file_view.write(request)
        return self._read()

    @staticmethod
    def _quote_special_chars(string):
        if ' ' in string or '\\\"' in string:
            return '"{}"'.format(string)
        else:
            return string

    def request(self, command, *args):
        if args is not None and len(args) > 0:
            args = [self._quote_special_chars(str(x).replace('"', '\\\"')) for x in args]
            print(args)
            arg_string = " ".join(args)
            print(arg_string)
            request = '{} {}\n'.format(command, arg_string)
        else:
            request = '{}\n'.format(command)
        self._file_view.write(request)
        return self._read()

    def stats(self):
        return self.request("stats")

    def status(self):
        return self.request("status")

    def find(self, *what):
        return self.request('find', what)

    def _read(self):
        return self._parse_response(self._get_response_utf8())

    def album_art(self, uri):
        request = "albumart {}\n".format(uri)
        info_dict = self._read_number_of_lines(2)
        print(info_dict)

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
        for i in range(0, number):
            response += self._file_view.read()
        return self._parse_response(response)

    def shutdown(self):
        self._file_view.close()
