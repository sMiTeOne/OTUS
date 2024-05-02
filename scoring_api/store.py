import tarantool
from tarantool.response import Response as TarantoolResponse


class Store:
    def __init__(self, space: str, host: str = 'localhost', port: int = 3301):
        self.connection = tarantool.connect(host=host, port=port).space(space)

    def get(self, primary_key: str) -> TarantoolResponse | None:
        return self.connection.select(primary_key)

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
