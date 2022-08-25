from typing import Any, Optional, Tuple, Dict
import logging
import os


logger = logging.getLogger(__name__)


class Configure:
    def __init__(self, config: Dict[str, Any]):
        self.config = config

    def get_option(
        self,
        default: Any,
        envkey: Optional[str] = None,
        config_path: Optional[Tuple[str]] = None,
        not_none: bool = False
    ) -> Any:
        env_value = None
        config_value = None
        if envkey:
            env_value = os.environ.get(envkey)
        if config_path and self.config:
            config_value = self.config
            for key in config_path:
                if not hasattr(config_value, '__getitem__'):
                    config_value = None
                    break
                config_value = config_value.get(key)

        value = env_value or config_value or default

        if not_none and value is None:
            raise ValueError('Option %s can not be None' % (envkey or ''))

        return value
