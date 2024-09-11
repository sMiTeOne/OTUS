from core import get_station_schedule_result
from store import StationStorage
from aiogram import (
    Bot,
    Dispatcher,
    executor,
)
from settings import TELEGRAM_API_TOKEN
from aiogram.types import (
    ParseMode,
    InlineQuery,
    InputTextMessageContent,
    InlineQueryResultArticle,
)

bot = Bot(token=TELEGRAM_API_TOKEN)
dp = Dispatcher(bot)
db = StationStorage()


@dp.inline_handler()
async def inline_echo(inline_query: InlineQuery) -> None:
    stations = db.search(inline_query.query.capitalize())[0]
    results = []
    for code, name in stations:
        message_text = await get_station_schedule_result(code)
        result = InlineQueryResultArticle(
            id=code,
            title=name,
            input_message_content=InputTextMessageContent(
                message_text=message_text,
                parse_mode=ParseMode.HTML,
            ),
        )
        results.append(result)
    await bot.answer_inline_query(inline_query.id, results=results, cache_time=1)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
