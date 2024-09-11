from enum import Enum


class StrEnum(str, Enum):
    def __str__(self) -> str:
        return str.__str__(self.value)


class ErrorTypes(StrEnum):
    data_retrieval_error = 'Не удалось получить расписание для запрошенной станции'
    missing_schedule_error = 'Нет расписания ближайщих поездов для запрошенной станции'


class ResponseFormat(StrEnum):
    json = 'json'
    xml = 'xml'


class ResponseLanguage(StrEnum):
    ru = 'ru_RU'
    ua = 'ua_UA'


class ContentTypes(StrEnum):
    json = 'application/json'
    html = 'text/html'


class TransportTypes(StrEnum):
    plane = 'plane'
    train = 'train'
    suburban = 'suburban'
    bus = 'bus'
    water = 'water'
    helicopter = 'helicopter'


class StationTypes(StrEnum):
    station = 'station'
    platform = 'platform'
    train_station = 'train_station'


class CountryTypes(StrEnum):
    ru = 'Россия'
