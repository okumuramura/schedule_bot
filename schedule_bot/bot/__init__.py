import logging
import toml


__log_format = r'[%(levelname)s] %(message)s'

logger = logging.Logger(__name__, logging.INFO)
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
handler.setFormatter(logging.Formatter(__log_format))
logger.addHandler(handler)


config = toml.load('./config.toml')
