"""Basic SAP modules infrastructure

The sub-modules rfc and adt should be independent on each other.
The sub-modules should not depend on any cli functionality.
All configuration must be achieved via dependency injection.

This module provides cli neutral functionality.
"""

import logging


def get_logger():
    """Returns the common logger object. Don't use for standard output"""

    return logging.getLogger()


__all__ = [
    "get_logger",
]
