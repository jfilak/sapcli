"""sapcli version and HTTP User-Agent identification

This module must not import other sap modules because it is used by
sap.config which is imported while the package sap is being initialized.
"""

import functools
import platform
from importlib.metadata import version, PackageNotFoundError

import requests.utils


def get_version():
    """Returns the installed sapcli version or 'unknown'"""

    try:
        return version('sapcli')
    except PackageNotFoundError:
        return 'unknown'


@functools.cache
def build_user_agent():
    """Returns the HTTP User-Agent value identifying sapcli, e.g.:
       sapcli/1.0.0 (Linux; x86_64; CPython 3.12.3) python-requests/2.32.3
    """

    return (f'sapcli/{get_version()} '
            f'({platform.system()}; {platform.machine()}; '
            f'{platform.python_implementation()} {platform.python_version()}) '
            f'{requests.utils.default_user_agent()}')
