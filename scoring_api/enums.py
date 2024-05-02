from enum import Enum


class Methods(str, Enum):
    OnlineScore = 'online_score'
    ClientsInterests = 'clients_interests'


class Genders(int, Enum):
    Unknown = 0
    Male = 1
    Female = 2


class HTTPStatus(int, Enum):
    UNKNOWN_ERROR = 0
    OK = 200
    BAD_REQUEST = 400
    FORBIDDEN = 403
    NOT_FOUND = 404
    INVALID_REQUEST = 422
    INTERNAL_ERROR = 500

    @property
    def label(self):
        return {
            0: "Unknown Error",
            400: "Bad Request",
            403: "Forbidden",
            404: "Not Found",
            422: "Invalid Request",
            500: "Internal Server Error",
        }.get(self, HTTPStatus.UNKNOWN_ERROR)
