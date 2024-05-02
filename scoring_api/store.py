import tarantool
from tarantool.response import Response as TarantoolResponse


class Cache:

    def __init__(self, space : str, host : str = 'localhost', port : int = 3301):
        self.host = host
        self.port = port
        self.space = space
        self.connection = None

    def cache_get(self, primary_key: str) -> TarantoolResponse | None:
        try:
            return self.connection.select(primary_key)
        except Exception:
            return None

    def cache_set(self, data: tuple) -> None:
        try:
            return self.connection.insert(data)
        except Exception:
            return None

    def initialize(self):
        self.connection = tarantool.connect(host=self.host, port=self.port).space(self.space)
