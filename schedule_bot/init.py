import asyncio

from api import get_station_list
from enums import (
    CountryTypes,
    StationTypes,
)
from store import StationStorage
from models import YandexRaspBaseRequest

db = StationStorage()


async def process_station(station: dict) -> None:
    if station['station_type'] in tuple(StationTypes):
        db.insert((station['codes']['yandex_code'], station['title']))


async def process_country(country: dict) -> None:
    for region in country['regions']:
        for settlement in region['settlements']:
            for station in settlement['stations']:
                await process_station(station)


async def init_stations() -> None:
    response_data = await get_station_list(YandexRaspBaseRequest())
    for country in response_data['countries']:
        if country['title'] in tuple(CountryTypes):
            await process_country(country)


asyncio.run(init_stations())
