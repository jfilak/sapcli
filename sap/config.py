"""Configuration"""

import os


def config_get(option: str, default: str = None) -> str:
    """Returns configuration values"""

    config = {'http_timeout': float(os.environ.get('SAPCLI_HTTP_TIMEOUT', 900))}

    return config.get(option, default)
