"""Basic SAP modules infrastructure

The sub-modules rfc and adt should be independent on each other.
The sub-modules should not depend on any cli functionality.
All configuration must be achieved via dependency injection.

This module provides cli neutral functionality.
"""

import os
import logging

from sap.config import config_get


def get_logger():
    """Returns the common logger object. Don't use for standard output"""

    logger = logging.getLogger()

    env_level = os.environ.get('SAPCLI_LOG_LEVEL', None)
    if env_level:
        logging.basicConfig()
        logger.setLevel(int(env_level))

    return logger


__all__ = [
    "get_logger",
]
