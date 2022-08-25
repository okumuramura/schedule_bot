import asyncio

from schedule_bot.updater import downloader


async def main() -> None:
    result = await downloader.hash_file('./updater/parse.py')
    print(result)


if __name__ == '__main__':
    result = asyncio.run(main())
