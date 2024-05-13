import os
import sys
from http import HTTPStatus
from datetime import datetime
from optparse import OptionParser
from socketserver import (
    TCPServer,
    BaseRequestHandler,
)

from enums import (
    RequestHeaders,
    RequestMethods,
)

INDEX_FILE = 'index.html'
SERVER_FOLDER = os.path.dirname(os.path.abspath(__file__))
ALLOWED_METHODS = set(RequestMethods)


class TCPHandler(BaseRequestHandler):
    def handle(self):
        recieved_data = str(self.request.recv(1024), 'utf-8')
        try:
            method, url, *_ = recieved_data.split()
        except ValueError:
            response = self._response(HTTPStatus.NOT_FOUND) + self._headers()
            self.request.sendall(response.encode())
            self.request.close()
            return None

        if method not in ALLOWED_METHODS:
            response = self._response(HTTPStatus.METHOD_NOT_ALLOWED) + self._headers()
            self.request.sendall(response.encode())
            self.request.close()
            return None

        if url.endswith('/'):
            url += INDEX_FILE

        file_path = SERVER_FOLDER + url
        if not os.path.exists(file_path):
            response = self._response(HTTPStatus.NOT_FOUND) + self._headers()
            self.request.send(response.encode('utf-8'))
            self.request.close()
            return None

        with open(file_path, encoding='utf-8') as file:
            file_data = file.read()
            response = self._response(HTTPStatus.OK) + self._headers(length=len(file_data)) + '\r\n' + file_data
            self.request.send(response.encode('utf-8'))
            self.request.close()
            return None

    def _response(self, http_status: HTTPStatus) -> str:
        return f'HTTP/1.1 {http_status.value} {http_status.name}\r\n'

    def _headers(self, length: int = 0) -> str:
        headers = {
            RequestHeaders.DATE: datetime.now().isoformat(),
            RequestHeaders.SERVER: 'localhost',
            RequestHeaders.CONNECTION: 'connection',
            RequestHeaders.CONTENT_TYPE: 'text/html; encoding=utf8',
            RequestHeaders.CONTENT_LENGTH: length,
        }
        return ''.join(f'{k}: {v}\r\n' for k, v in headers.items())


class Server(TCPServer):
    allow_reuse_address = True

    def __init__(self, server_address, handler):
        TCPServer.__init__(self, server_address, handler)


if __name__ == "__main__":
    op = OptionParser()
    op.add_option("-r", "--root", action="store", default=SERVER_FOLDER)
    opts, args = op.parse_args()

    address = ('localhost', 80)
    server = Server(address, TCPHandler)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        sys.exit(0)
