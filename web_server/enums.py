from enum import Enum


class RequestMethods(str, Enum):
    GET = 'GET'
    HEAD = 'HEAD'


class RequestHeaders(str, Enum):
    DATE = 'Date'
    SERVER = 'Server'
    CONTENT_TYPE = 'Content-Type'
    CONTENT_LENGTH = 'Content-Length'