from hashlib import md5
from typing import Optional

from aioredis import Redis

from schedule_bot import REDIS_HOST, REDIS_PORT


class FilesStorage:
    prefix = 'file_'

    def __init__(self) -> None:
        self.redis = Redis(host=REDIS_HOST, port=REDIS_PORT)

    def __keyify(self, file: str) -> str:
        file_hash = md5(file.encode('utf-8')).hexdigest()
        return f'{self.prefix}{file_hash}'

    async def set(self, file: str, hash: str) -> None:
        await self.redis.set(
            self.__keyify(file),
            hash,
        )

    async def get(self, file: str) -> Optional[str]:
        value: Optional[bytes] = await self.redis.get(self.__keyify(file))
        if value is None:
            return None
        return value.decode('utf-8')

    async def getset(self, file: str, hash: str) -> Optional[str]:
        value: Optional[bytes] = await self.redis.getset(
            self.__keyify(file), hash
        )
        if value is None:
            return None
        return value.decode('utf-8')
