import asyncio
import os
from os import path

import aiohttp
import requests
from bs4 import BeautifulSoup


def download(dest = "./"):
    os.makedirs(dest, exist_ok = True)
    schedule_page = r"https://istu.ru/material/raspisanie-zanyatiy"
    main_page = r"https://istu.ru/"
    page = requests.get(schedule_page)
    links = []

    if page.status_code == 200:
        soup = BeautifulSoup(page.text.encode("utf-8"), "html.parser")
        table = soup.find("table", attrs= {"class": "istu-table"}).find("tbody")
        hrefs = table.find_all("a", href = True)
        for href in hrefs:
            link = href["href"]
            links.append(main_page + link)
        filenames = list(map(lambda l: l.split("/")[-1], links))

        if os.name == "nt":
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

        sem = asyncio.Semaphore(4)
        async def download_file(link, name, dest = dest):
            async with sem, aiohttp.ClientSession() as session:
                async with session.get(link) as source:
                    data = await source.read()
                
            with open(path.join(dest, name), "wb") as file:
                file.write(data)

        loop = asyncio.get_event_loop()
        tasks = [loop.create_task(download_file(link, name)) for link, name in zip(links, filenames)]
        loop.run_until_complete(asyncio.wait(tasks))
        loop.close()
        return list(map(lambda name: path.join(dest, name), filenames))
    return False

if __name__ == "__main__":
    files = download("./FILES")
    with open("files.txt", "w", encoding="utf-8") as file:
        for f in files:
            file.write(f)
            file.write("\n")
