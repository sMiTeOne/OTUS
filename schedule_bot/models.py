from enums import (
    ResponseFormat,
    ResponseLanguage,
    TransportTypes,
)
from datetime import datetime
from pydantic import (
    BaseModel,
    field_validator,
)
from settings import YANDEX_API_TOKEN


class YandexRaspBaseRequest(BaseModel):
    apikey: str = YANDEX_API_TOKEN
    format: ResponseFormat = ResponseFormat.json
    lang: ResponseLanguage = ResponseLanguage.ru


class StationScheduleRequest(YandexRaspBaseRequest):
    station: str
    date: str = datetime.now().strftime("%Y-%m-%d")
    transport_types: TransportTypes = TransportTypes.suburban


class ScheduleThread(BaseModel):
    uid: str
    short_title: str


class StationScheduleItem(BaseModel):
    direction: str
    departure: str
    thread: ScheduleThread

    @field_validator('departure', mode='before')
    @classmethod
    def get_departure_time(cls, departure: str | None) -> str:
        return departure[11:16] if departure else ''


class StationScheduleResponse(BaseModel):
    schedule: list[StationScheduleItem]
