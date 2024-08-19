import os
import uuid
import asyncio
import logging
from http import HTTPStatus

import aiohttp
import aiofiles
import settings
from bs4 import BeautifulSoup

DOWNLOAD_QUEUE = asyncio.Queue()
COMMENTS_QUEUE = asyncio.Queue()


async def get(session: aiohttp.ClientSession, url: str) -> bytes | None:
    try:
        async with session.get(url, timeout=settings.CONNECTION_TIMEOUT) as response:
            if response.status != HTTPStatus.OK:
                logging.warning('Failed to load page %s', url)
            return await response.content.read()
    except asyncio.TimeoutError:
        logging.error('Timeout error requesting %s', url)
    except aiohttp.client_exceptions.ClientConnectionError:
        logging.error('Unable to access the url %s', url)


async def download_news(session: aiohttp.ClientSession, news: dict) -> None:
    async with asyncio.Semaphore(settings.CONNECTION_MAX_COUNT):
        if content := await get(session, news['url']):
            await save_file(news['path'], content)


async def save_file(file_path: str, data: bytes) -> None:
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    async with aiofiles.open(file_path, "wb") as file:
        await file.write(data)


def is_news_exist(news_id: str) -> bool:
    news_path = os.path.join(settings.STORAGE_FOLDER, news_id)
    return os.path.exists(news_path)


def is_external_link(url: str) -> bool:
    return 'http://' in url or 'https://' in url


async def parse_main_page(response: str) -> None:
    soup = BeautifulSoup(response, "html.parser")
    news = soup.find_all('tr', class_='athing')

    for news in news:
        if is_news_exist(news_id=news['id']):
            logging.info('News %s already exist. Skipping...', news['id'])
            continue

        news_url = news.find('span', class_='titleline').a['href']

        if news_url == f'item?id={news["id"]}':
            logging.info('News %s is comment. Skipping...', news['id'])
            continue

        comments_url = f'{settings.CRAWLABLE_URL}/item?id={news["id"]}'
        path = os.path.join(settings.STORAGE_FOLDER, news['id'], 'main.html')

        await DOWNLOAD_QUEUE.put({'url': news_url, 'path': path})
        await COMMENTS_QUEUE.put({'url': comments_url, 'news_id': news['id']})


async def parse_comment_page(response: str, news_id: str) -> None:
    soup = BeautifulSoup(response, "html.parser")
    comments = soup.find_all('div', class_='comment')

    for comment in comments:
        urls = comment.find_all('a')
        for url in urls:
            comment_url = url['href']
            if is_external_link(comment_url):
                file_name = f'{uuid.uuid4()}.html'
                path = os.path.join(settings.STORAGE_FOLDER, news_id, file_name)
                await DOWNLOAD_QUEUE.put({'url': comment_url, 'path': path})


async def main_loop(session: aiohttp.ClientSession) -> None:
    while True:
        response = await get(session=session, url=settings.CRAWLABLE_URL)
        await parse_main_page(response=response)
        logging.info('Waiting %s seconds', settings.SCHEDULE_INTERVAL)
        await asyncio.sleep(settings.SCHEDULE_INTERVAL)


async def comments_loop(session: aiohttp.ClientSession) -> None:
    while True:
        comment = await COMMENTS_QUEUE.get()
        response = await get(session=session, url=comment['url'])
        await parse_comment_page(response=response, news_id=comment['news_id'])


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
