import os
import uuid
import asyncio
import logging
from http import HTTPStatus

import aiohttp
import aiofiles
import settings
from bs4 import BeautifulSoup
from models import (
    Comment,
    News
)

DOWNLOAD_QUEUE = asyncio.Queue()
COMMENTS_QUEUE = asyncio.Queue()

URL = 'https://news.ycombinator.com'

async def get(session: aiohttp.ClientSession, url: str) -> bytes | None:
    try:
        response = await session.get(url, timeout=settings.CONNECTION_TIMEOUT)
        if response.status != HTTPStatus.OK:
            logging.warning('Failed to load page %s', url)
    except asyncio.TimeoutError:
        logging.error('Timeout error requesting %s', url)
    except aiohttp.client_exceptions.ClientConnectionError:
        logging.error('Unable to access the url %s', url)
    else:
        return await response.content.read()


async def download_news(session: aiohttp.ClientSession, news: News) -> None:
    async with asyncio.Semaphore(settings.DOWNLOADING_CONCURRENCY):
        if content := await get(session, news.url):
            await save_file(news.file_path, content)


async def save_file(file_path: str, data: bytes) -> None:
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    async with aiofiles.open(file_path, "wb") as file:
        await file.write(data)


async def parse_main_page(response: str) -> None:
    soup = BeautifulSoup(response, "html.parser")
    news = soup.find_all('tr', class_='athing')

    for news in news:
        news_id = news['id']
        folder_path = f'{settings.STORAGE_FOLDER}/{news_id}'
        if os.path.exists(folder_path):
            logging.info('News %s already exist. Skipping...', news_id)
            continue

        news_url: str = news.find('span', class_='titleline').a['href']
        if not news_url.startswith('http'):
            logging.info('News %s is comment. Skipping...', news_id)
            continue

        comments_url = f'{URL}?id={news_id}'
        file_path = f'{folder_path}/main.html'

        await DOWNLOAD_QUEUE.put(News(url=news_url, file_path=file_path))
        await COMMENTS_QUEUE.put(Comment(url=comments_url, news_id=news_id))


async def parse_comment_page(response: str, news_id: str) -> None:
    soup = BeautifulSoup(response, "html.parser")
    comments = soup.find_all('div', class_='comment')

    for comment in comments:
        urls = comment.find_all('a')
        for url in urls:
            comment_url: str = url['href']
            if comment_url.startswith('http'):
                file_name = f'{uuid.uuid4()}.html'
                file_path = f'{settings.STORAGE_FOLDER}/{news_id}/{file_name}'
                await DOWNLOAD_QUEUE.put(News(url=comment_url, file_path=file_path))


async def main_loop(session: aiohttp.ClientSession) -> None:
    while True:
        response = await get(session=session, url=URL)
        await parse_main_page(response=response)
        logging.info('Waiting %s seconds', settings.SCHEDULE_INTERVAL)
        await asyncio.sleep(settings.SCHEDULE_INTERVAL)


async def comments_loop(session: aiohttp.ClientSession) -> None:
    while True:
        comment: Comment = await COMMENTS_QUEUE.get()
        response = await get(session=session, url=comment.url)
        await parse_comment_page(response=response, news_id=comment.news_id)


async def download_loop(session: aiohttp.ClientSession) -> None:
    while True:
        news = await DOWNLOAD_QUEUE.get()
        asyncio.create_task(download_news(session, news))


async def main() -> None:
    connector = aiohttp.TCPConnector(ssl=False)
    async with aiohttp.ClientSession(connector=connector) as session:
        await asyncio.gather(
            main_loop(session),
            download_loop(session),
            comments_loop(session),
        )


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        datefmt='%Y.%m.%d %H:%M:%S',
        format='[%(asctime)s] %(levelname).1s %(message)s',
    )

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Stop application")
