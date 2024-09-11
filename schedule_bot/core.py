from datetime import datetime
from collections import defaultdict

from api import get_station_schedule
from enums import ErrorTypes
from models import (
    StationScheduleRequest,
    StationScheduleResponse,
)
from async_lru import alru_cache

YANDEX_RASP_URL = 'https://rasp.yandex.ru/thread/'


@alru_cache(maxsize=32)
async def get_station_schedule_result(station: str) -> str:
    current_time = datetime.now().strftime('%H:%M')
    request = StationScheduleRequest(station=station)
    response = await get_station_schedule(request)
    if 'error' in response:
        return ErrorTypes.data_retrieval_error
    else:
        response = StationScheduleResponse(**response)

    result = defaultdict(list)
    for schedule in response.schedule:
        if schedule.departure > current_time:
            schedule_row = f'<a href="{YANDEX_RASP_URL}{schedule.thread.uid}">{schedule.departure}</a> | {schedule.thread.short_title}'
            result[schedule.direction].append(schedule_row)
    if not result:
        return ErrorTypes.missing_schedule_error

    text_result = ''
    for direction, schedule in result.items():
        schedule = '\n'.join(schedule)
        text_result += f'''
<b>{direction}</b>

Отпр. | Маршрут
{schedule}
'''

    return text_result
