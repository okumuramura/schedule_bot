import logging
import logging.config

import toml
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from schedule_bot.utils.configure import Configure


logging.config.fileConfig('./logger.conf', disable_existing_loggers=False)
logger = logging.getLogger(__name__)

config = toml.load('config.toml')

configure = Configure(config)

REDIS_HOST: str = configure.get_option('localhost', 'REDIS_HOST', config, ('redis', 'host'))
REDIS_PORT: int = configure.get_option(6379, 'REDIS_PORT', ('redis', 'port'))
TELEGRAM_KEY: str = configure.get_option(None, 'TELEGRAM_KEY', ('bot', 'key'), not_none=True)
WEATHER_KEY: str = configure.get_option(None, 'WEATHER_KEY', ('tools', 'weather', 'key'))
DB_HOST: str = configure.get_option(None, 'DB_HOST', ('db', 'host'), not_none=True)
DB_DRIVER: str = configure.get_option(None, 'DB_DRIVER', ('db', 'driver'), not_none=True)

logger.debug('REDIS HOST: %s', REDIS_HOST)
logger.debug('REDIS PORT: %s', REDIS_PORT)
logger.debug('TELEGRAM KEY: %s', TELEGRAM_KEY)
logger.debug('WEATHER_KEY: %s', WEATHER_KEY)
logger.debug('DB HOST: %s', DB_HOST)
logger.debug('DB DRIVER: %s', DB_DRIVER)


engine = create_engine(f'{DB_DRIVER}://{DB_HOST}')
Base = declarative_base()
Session = sessionmaker(bind=engine, expire_on_commit=False)
