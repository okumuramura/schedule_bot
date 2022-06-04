import logging
import logging.config

logging.config.fileConfig(
    './scedule_bot/logger.conf', disable_existing_loggers=False
)
logger = logging.getLogger(__name__)
