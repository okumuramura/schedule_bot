import logging
import os
from typing import Any, Dict, Optional, Tuple

logger = logging.getLogger(__name__)


class Configure:
    def __init__(self, config: Dict[str, Any]) -> None:
        self.config = config

    def get_option(
        self,
        default: Any,
        envkey: Optional[str] = None,
        config_path: Optional[Tuple[str, ...]] = None,
        not_none: bool = False,
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
                config_value = config_value.get(key)  # type: ignore

        value = env_value or config_value or default

        config_path_str = ''
        if config_path:
            config_path_str = '.'.join(config_path)

        if not_none and value is None:
            raise ValueError(
                'Option %s can not be None' % (envkey or config_path_str or '')
            )

        logger.debug(
            'Config option %s has value %r',
            (envkey or config_path_str or ''),
            value,
        )
        return value
