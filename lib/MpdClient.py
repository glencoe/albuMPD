class MpdClient:

    def __init__(self, file_view):
        self._file_view = file_view

    def connect(self, host, port):
        self._file_view.connect(host, port)
        print(self._file_view.read())

    def list(self, what, group_tag=None, filter=None):
        request = "list " + what + "\n"
        self._file_view.write(request)
        return self._get_response_utf8()

    def _get_response_utf8(self):
        response = ""
        end_of_transmission = False
        while not end_of_transmission:
            line = self._file_view.read()
            if line.startswith("OK\n"):
                end_of_transmission = True
            else:
                response += line
        return response
