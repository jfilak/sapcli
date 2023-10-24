"""Base RFC functionality"""


from typing import Any, Dict

import sap
import sap.errors

from sap.rfc.errors import RFCLoginError, RFCCommunicationError


RFCParams = Dict[str, Any]
RFCResponse = Dict[str, Any]


SAPRFC_MODULE = None


def mod_log():
    """rfc.core module logger"""

    return sap.get_logger()


def _try_import_pyrfc():

    # pylint: disable=global-statement
    global SAPRFC_MODULE

    try:
        import pyrfc
    except ImportError as ex:
        mod_log().info('Failed to import the module pyrfc')
        mod_log().debug(str(ex))
    else:
        SAPRFC_MODULE = pyrfc


def _unimport_pyrfc():
    """For the sake of testing"""

    # pylint: disable=global-statement
    global SAPRFC_MODULE

    SAPRFC_MODULE = None


def rfc_is_available():
    """Returns true if RFC can be used"""

    if SAPRFC_MODULE is None:
        _try_import_pyrfc()

    return SAPRFC_MODULE is not None


def _assert_rfc_availability():
    if not rfc_is_available():
        raise sap.errors.SAPCliError(
            'RFC functionality is not available(enabled)')


def connect(**kwargs):
    """SAP RFC Connection.
    """

    _assert_rfc_availability()

    mod_log().info('Connecting via SAP rfc with params %s', kwargs)
    # pylint: disable=protected-access
    try:
        return SAPRFC_MODULE.Connection(**kwargs)
    except SAPRFC_MODULE._exception.LogonError as exc:
        raise RFCLoginError(kwargs['ashost'], kwargs['user'], exc) from exc
    except SAPRFC_MODULE._exception.CommunicationError as exc:
        raise RFCCommunicationError(kwargs['ashost'], kwargs['user'], exc) from exc


def try_pyrfc_exception_type():
    """SAP RFC Exception type.
    """

    _assert_rfc_availability()

    # pylint: disable=protected-access
    return SAPRFC_MODULE._exception.RFCLibError
