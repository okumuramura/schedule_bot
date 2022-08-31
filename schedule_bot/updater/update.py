import asyncio

from schedule_bot.updater import downloader


async def main() -> None:
    result = await downloader.hash_file(__file__)
    print(result)


if __name__ == '__main__':
    result = asyncio.run(main())
