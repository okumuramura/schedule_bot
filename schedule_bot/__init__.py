import logging
import logging.config

import toml
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

logging.config.fileConfig('./logger.conf', disable_existing_loggers=False)
logger = logging.getLogger(__name__)

engine = create_engine('sqlite:///lessons.db')
Base = declarative_base()
Session = sessionmaker(bind=engine, expire_on_commit=False)

config = toml.load('config.toml')
