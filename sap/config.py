"""Configuration"""

import os
from typing import Any


def config_get(option: str, default: Any = None) -> Any:
    """Returns configuration values"""

    config = {'http_timeout': float(os.environ.get('SAPCLI_HTTP_TIMEOUT', 900))}

    return config.get(option, default)
