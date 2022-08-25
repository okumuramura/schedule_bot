import logging
import logging.config
from typing import List

import toml
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from schedule_bot.utils.configure import Configure

logging.config.fileConfig('./logger.conf', disable_existing_loggers=False)
logger = logging.getLogger(__name__)

config = toml.load('config.toml')

configure = Configure(config)

REDIS_HOST: str = configure.get_option(
    'localhost', 'REDIS_HOST', config, ('redis', 'host')
)
REDIS_PORT: int = configure.get_option(6379, 'REDIS_PORT', ('redis', 'port'))
TELEGRAM_KEY: str = configure.get_option(
    None, 'TELEGRAM_KEY', ('bot', 'key'), not_none=True
)
WEATHER_KEY: str = configure.get_option(
    None, 'WEATHER_KEY', ('tools', 'weather', 'key')
)
DB_HOST: str = configure.get_option(
    None, 'DB_HOST', ('db', 'host'), not_none=True
)
DB_DRIVER: str = configure.get_option(
    None, 'DB_DRIVER', ('db', 'driver'), not_none=True
)
WEATHER_LOCATION: int = configure.get_option(
    296181, 'WEATHER_LOCATION', ('tools', 'weather', 'location')
)
BOT_ADMINS: List[int] = configure.get_option([], config_path=('bot', 'admins'))


DB_URL = f'{DB_DRIVER}://{DB_HOST}'

engine = create_engine(DB_URL)
Base = declarative_base()
Session = sessionmaker(bind=engine, expire_on_commit=False)
