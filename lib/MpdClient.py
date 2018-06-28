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
        self.command(request)
        return self._read()

    def command(self, request):
        request += "\n"
        self._file_view.write(request)
        return self._read()

    def stats(self):
        self.command("stats")
        return self._read()

    def _read(self):
        return self._parse_response(self._get_response_utf8())

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

    def shutdown(self):
        self._file_view.close()
