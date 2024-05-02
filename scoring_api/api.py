#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import uuid
import hashlib
import logging
from datetime import datetime as dt
from optparse import OptionParser
from http.server import (
    HTTPServer,
    BaseHTTPRequestHandler,
)

from enums import (
    Methods,
    HTTPStatus,
)
from models import (
    MethodRequest,
    OnlineScoreRequest,
    ClientsInterestsRequest,
)

SALT = "Otus"
ADMIN_LOGIN = "admin"
ADMIN_SALT = "42"


def check_auth(request: dict) -> bool:
    if ADMIN_LOGIN == request['login']:
        raw_string = dt.now().strftime("%Y%m%d%H") + ADMIN_SALT
    else:
        raw_string = request['account'] + request['login'] + SALT
    return hashlib.sha512(raw_string.encode('utf-8')).hexdigest() == request['token']


def method_handler(request: dict, context: dict, store):
    response, code = None, HTTPStatus.OK
    request_payload = request['body']
    request_method = MethodRequest(request_payload)
    request_method.validate_request()
    if request_method.errors:
        return request_method.errors, HTTPStatus.INVALID_REQUEST
    if not check_auth(request_payload):
        return 'Unauthorized', HTTPStatus.FORBIDDEN

    arguments = request_payload['arguments']
    match request_payload['method']:
        case Methods.OnlineScore:
            request_method = OnlineScoreRequest(arguments)
            context.update(
                has=arguments.keys(),
                login=request_payload['login'],
            )
            return request_method.execute(arguments, context)
        case Methods.ClientsInterests:
            request_method = ClientsInterestsRequest(arguments)
            return request_method.execute(arguments, context)
        case _:
            return response, code


class MainHTTPHandler(BaseHTTPRequestHandler):
    router = {"method": method_handler}
    store = None

    def get_request_id(self, headers):
        return headers.get('HTTP_X_REQUEST_ID', uuid.uuid4().hex)

    def do_POST(self):
        response, code = {}, HTTPStatus.OK
        context = {"request_id": self.get_request_id(self.headers)}
        request = None
        try:
            data_string = self.rfile.read(int(self.headers['Content-Length']))
            request = json.loads(data_string)
        except Exception:
            code = HTTPStatus.BAD_REQUEST

        if request:
            path = self.path.strip("/")
            logging.info("%s: %s %s" % (self.path, data_string, context["request_id"]))
            if path in self.router:
                try:
                    response, code = self.router[path]({"body": request, "headers": self.headers}, context, self.store)
                except Exception as e:
                    logging.exception("Unexpected error: %s" % e)
                    code = HTTPStatus.INTERNAL_ERROR
            else:
                code = HTTPStatus.NOT_FOUND

        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        if code == HTTPStatus.OK:
            r = {"response": response, "code": code}
        else:
            r = {"error": response or HTTPStatus(code).label, "code": code}
        context.update(r)
        logging.info(context)
        self.wfile.write(str.encode(json.dumps(r)))


if __name__ == "__main__":
    op = OptionParser()
    op.add_option("-p", "--port", action="store", type=int, default=8080)
    op.add_option("-l", "--log", action="store", default=None)
    (opts, args) = op.parse_args()
    logging.basicConfig(
        filename=opts.log,
        level=logging.INFO,
        format='[%(asctime)s] %(levelname).1s %(message)s',
        datefmt='%Y.%m.%d %H:%M:%S',
    )
    server = HTTPServer(("localhost", opts.port), MainHTTPHandler)
    logging.info("Starting server at %s" % opts.port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()
