import tarantool
from tarantool.response import Response
from settings import (
    STORAGE_DB_NAME,
    STORAGE_DB_HOST,
    STORAGE_DB_PORT
)


class StationStorage:
    def __init__(
        self,
        space: str = STORAGE_DB_NAME,
        host: str = STORAGE_DB_HOST,
        port: int = STORAGE_DB_PORT,
    ):
        self.space = space
        self.host = host
        self.port = port
        self.connection = tarantool.connect(host=self.host, port=self.port).space(self.space)

    def select(self, code: str) -> Response | None:
        try:
            return self.connection.select(code)
        except Exception:
            return None

    def search(self, name: str) -> Response | None:
        try:
            return self.connection.call('search', name)
        except Exception:
            return None

    def insert(self, data: tuple) -> None:
        try:
            return self.connection.insert(data)
        except Exception:
            return None
