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

from enums import Methods
from models import *

from scoring import (
    get_score,
    get_interests,
)

SALT = "Otus"
ADMIN_LOGIN = "admin"
ADMIN_SALT = "42"
OK = 200
BAD_REQUEST = 400
FORBIDDEN = 403
NOT_FOUND = 404
INVALID_REQUEST = 422
INTERNAL_ERROR = 500
ERRORS = {
    BAD_REQUEST: "Bad Request",
    FORBIDDEN: "Forbidden",
    NOT_FOUND: "Not Found",
    INVALID_REQUEST: "Invalid Request",
    INTERNAL_ERROR: "Internal Server Error",
}
ONLINE_SCORE_PAIRS = (
    {'phone', 'email'},
    {'gender', 'birthday'},
    {'first_name', 'last_name'},
)


def check_auth(request: dict) -> bool:
    if ADMIN_LOGIN == request['login']:
        raw_string = dt.now().strftime("%Y%m%d%H") + ADMIN_SALT
    else:
        raw_string = request['account'] + request['login'] + SALT

    return hashlib.sha512(raw_string.encode('utf-8')).hexdigest() == request['token']


def method_handler(request: dict, context: dict, store):
    response, code = None, OK
    request_payload = request['body']
    request_method = MethodRequest(request_payload)

    request_method.validate_request()
    if request_method.errors:
        return request_method.errors, INVALID_REQUEST

    if not check_auth(request_payload):
        return None, FORBIDDEN

    login = request_payload['login']
    method = request_payload['method']
    arguments = request_payload['arguments']

    if not (request_method_class := METHODS_MAPPING.get(method)):
        return f'Method {method} is not supported', INVALID_REQUEST

    request_method: Serializer = request_method_class(arguments)
    request_method.validate_request()
    if request_method.errors:
        return request_method.errors, INVALID_REQUEST

    match method:
        case Methods.OnlineScore:
            has = set(arguments.keys())
            context["has"] = list(has)
            if not any((pair <= has for pair in ONLINE_SCORE_PAIRS)):
                return 'Missing pairs of fields', INVALID_REQUEST
            score = 42 if login == ADMIN_LOGIN else get_score(store, **request_payload['arguments'])
            response = {'score': score}
        case Methods.ClientsInterests:
            context["nclients"] = len(arguments['client_ids'])
            response = {client_id: get_interests(store, context) for client_id in arguments['client_ids']}
    return response, code


class MainHTTPHandler(BaseHTTPRequestHandler):
    router = {"method": method_handler}
    store = None

    def get_request_id(self, headers):
        return headers.get('HTTP_X_REQUEST_ID', uuid.uuid4().hex)

    def do_POST(self):
        response, code = {}, OK
        context = {"request_id": self.get_request_id(self.headers)}
        request = None
        try:
            data_string = self.rfile.read(int(self.headers['Content-Length']))
            request = json.loads(data_string)
        except Exception:
            code = BAD_REQUEST

        if request:
            path = self.path.strip("/")
            logging.info("%s: %s %s" % (self.path, data_string, context["request_id"]))
            if path in self.router:
                try:
                    response, code = self.router[path]({"body": request, "headers": self.headers}, context, self.store)
                except Exception as e:
                    logging.exception("Unexpected error: %s" % e)
                    code = INTERNAL_ERROR
            else:
                code = NOT_FOUND

        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        if code not in ERRORS:
            r = {"response": response, "code": code}
        else:
            r = {"error": response or ERRORS.get(code, "Unknown Error"), "code": code}
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
