import asyncio
import hashlib
import os
from pathlib import Path
from typing import List

import aiohttp
import aiofiles
import requests
from bs4 import BeautifulSoup

from schedule_bot.updater import logger
from schedule_bot.updater.storage import FilesStorage

storage = FilesStorage()


async def hash_bytes(bytes: bytes) -> str:
    sha1 = hashlib.sha1(bytes)

    return sha1.hexdigest()


async def hash_file(path: str) -> str:
    BUFFER_SIZE = 65536  # 64 mb
    sha1 = hashlib.sha1()

    async with aiofiles.open(path, 'rb') as file:
        while file_bytes := await file.read(BUFFER_SIZE):
            sha1.update(file_bytes)

    return sha1.hexdigest()


async def download(dest: str = './') -> List[str]:
    dest_path = Path(dest)
    dest_path.mkdir(parents=True, exist_ok=True)
    schedule_page = r"https://istu.ru/material/raspisanie-zanyatiy"
    main_page = r"https://istu.ru/"
    page = requests.get(schedule_page)
    links = []

    if page.status_code == 200:
        soup = BeautifulSoup(page.text.encode("utf-8"), "html.parser")
        table = soup.find("table", attrs={"class": "istu-table"}).find("tbody")
        hrefs = table.find_all("a", href=True)
        for href in hrefs:
            link = href["href"]
            links.append(main_page + link)

        logger.info('Fetch %d files. Downloading...', len(links))
        filenames = list(map(lambda l: l.split("/")[-1], links))

        if os.name == "nt":
            logger.debug('Using Windows event loop policy')
            asyncio.set_event_loop_policy(
                asyncio.WindowsSelectorEventLoopPolicy()
            )

        sem = asyncio.Semaphore(4)

        async def download_file(
            link: str, name: str, dest: Path = dest_path
        ) -> None:
            logger.info('Downloading %s', name)
            async with sem, aiohttp.ClientSession() as session:
                async with session.get(link) as source:
                    data = await source.read()

            file_hash = await hash_bytes(data)
            stored_file_hash = await storage.get(name)
            save = (dest / name).exists() or file_hash != stored_file_hash
            logger.info(
                "File hash (%s): %s %s",
                name,
                file_hash,
                '(skip)' if not save else '',
            )

            if save:
                await storage.set(name, file_hash)
                async with aiofiles.open(dest / name, "wb") as file:
                    await file.write(data)

        tasks = [
            asyncio.create_task(download_file(link, name))
            for link, name in zip(links, filenames)
        ]
        await asyncio.gather(*tasks)
        logger.info('Finished')
        return list(map(lambda name: dest_path / name, filenames))
    return []


if __name__ == "__main__":
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    asyncio.run(download('./FILES'))
