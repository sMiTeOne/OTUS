import aiohttp
from enums import ContentTypes
from models import (
    YandexRaspBaseRequest,
    StationScheduleRequest,
)
from settings import YANDEX_API_ADDESS


async def get_station_schedule(params: StationScheduleRequest) -> dict:
    """Возвращает список поездов, отправляющихся от указанной станции"""
    async with aiohttp.ClientSession() as session:
        async with session.get(f'{YANDEX_API_ADDESS}/schedule', params=params.dict()) as response:
            return await response.json(content_type=ContentTypes.json)


async def get_station_list(params: YandexRaspBaseRequest) -> dict:
    """Возвращает полный список станций"""
    async with aiohttp.ClientSession() as session:
        async with session.get(f'{YANDEX_API_ADDESS}/stations_list', params=params.dict()) as response:
            return await response.json(content_type=ContentTypes.html)
