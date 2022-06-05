import logging
import logging.config

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

logging.config.fileConfig(
    './scedule_bot/logger.conf', disable_existing_loggers=False
)
logger = logging.getLogger(__name__)

engine = create_engine('sqlite:///lessons.db')
Base = declarative_base()
Session = sessionmaker(bind=engine, expire_on_commit=False)
