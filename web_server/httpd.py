import os
import sys
from http import HTTPStatus
from datetime import datetime
from optparse import OptionParser
from socketserver import (
    TCPServer,
    BaseRequestHandler,
)
from urllib.parse import unquote

from enums import (
    RequestHeaders,
    RequestMethods,
    RequestContentType,
)

INDEX_FILE = 'index.html'
SERVER_FOLDER = os.path.dirname(os.path.abspath(__file__))
ALLOWED_METHODS = set(RequestMethods)


class TCPHandler(BaseRequestHandler):
    def handle(self):
        received_data = str(self.request.recv(1024), 'utf-8')
        try:
            method, url, *_ = received_data.split()
            url = self._normalize_url(url)
        except ValueError:
            response = self._response(HTTPStatus.NOT_FOUND)
            self.request.send(response + self._headers())
            self.request.close()
            return None

        if method not in ALLOWED_METHODS:
            response = self._response(HTTPStatus.METHOD_NOT_ALLOWED)
            self.request.send(response + self._headers())
            self.request.close()
            return None

        file_path = SERVER_FOLDER + url
        if not os.path.exists(file_path):
            response = self._response(HTTPStatus.NOT_FOUND)
            self.request.send(response + self._headers())
            self.request.close()
            return None

        with open(file_path, 'rb') as file:
            file_data = file.read()
            response = self._response(HTTPStatus.OK)
            headers = self._headers(
                content_type=self._content_type(file.name),
                content_length=len(file_data),
            )

            if method == RequestMethods.HEAD:
                file_data = b''

            self.request.send(response + headers + file_data)
            self.request.close()
            return None

    def _response(self, http_status: HTTPStatus) -> str:
        return f'HTTP/1.1 {http_status.value} {http_status.phrase}\r\n'.encode()

    def _headers(self, content_type: str = 'text/html', content_length: int = 0) -> str:
        headers = {
            RequestHeaders.DATE: datetime.now().isoformat(),
            RequestHeaders.SERVER: 'localhost',
            RequestHeaders.CONNECTION: 'connection',
            RequestHeaders.CONTENT_TYPE: content_type,
            RequestHeaders.CONTENT_LENGTH: content_length,
        }
        return (''.join(f'{k}: {v}\r\n' for k, v in headers.items()) + '\r\n').encode()

    def _content_type(self, file_path: str) -> str:
        file_extension = file_path[file_path.rfind('.') + 1 :]
        return RequestContentType[file_extension].value

    def _normalize_url(self, url: str) -> str:
        url = unquote(url)
        if '?' in url:
            url = url[: url.find('?')]
        if url.endswith('/'):
            url = url.removesuffix('/')
            file_name = url[url.rfind('/') + 1 :]
            url += '/' + ('' if '.' in file_name else INDEX_FILE)
        return url


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
