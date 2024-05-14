from enum import Enum


class RequestMethods(str, Enum):
    GET = 'GET'
    HEAD = 'HEAD'


class RequestHeaders(str, Enum):
    DATE = 'Date'
    SERVER = 'Server'
    CONNECTION = 'Connection'
    CONTENT_TYPE = 'Content-Type'
    CONTENT_LENGTH = 'Content-Length'


class RequestContentType(str, Enum):
    txt = 'text/plain'
    html = 'text/html'
    css = 'text/css'
    js = 'text/javascript'
    jpg = 'image/jpeg'
    jpeg = 'image/jpeg'
    png = 'image/png'
    gif = 'image/gif'
    swf = 'application/x-shockwave-flash'
