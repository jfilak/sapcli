"""BAPI helpers and utilities"""

from typing import Union, List

from sap.errors import SAPCliError
from sap.rfc.core import RFCResponse


BAPIReturnRFC = Union[RFCResponse, List[RFCResponse]]


def bapi_message_to_str(bapiret: RFCResponse):
    """Converts a single BAPI return value to a human readable string"""

    return '/'.join([bapiret['TYPE'], bapiret['ID'], bapiret['NUMBER'] + ': ' + bapiret['MESSAGE']])


class BAPIReturn:
    """BAPI return value"""

    def __init__(self, bapi_return: BAPIReturnRFC):
        if isinstance(bapi_return, dict):
            self._bapirettab = [bapi_return]
        elif isinstance(bapi_return, list):
            self._bapirettab = bapi_return
        else:
            raise ValueError(f'Neither dict nor list BAPI return type: {type(bapi_return).__name__}')

        for bapiret in self._bapirettab:
            if bapiret['TYPE'] == 'E':
                self._error_message = bapi_message_to_str(bapiret)
                break
        else:
            self._error_message = None

    def __str__(self):
        return '\n'.join([bapi_message_to_str(bapiret) for bapiret in self._bapirettab])

    def __getitem__(self, index):
        return self._bapirettab[index]

    def contains(self, msg_class, msg_number):
        """"Returns True if the list of messages contains specified Message
            Class and Message Number.
        """

        return any((msg['ID'] == msg_class and msg['NUMBER'] == msg_number for msg in self._bapirettab))

    @property
    def is_error(self):
        """Returns True if the BAPI response represents an error.
           Otherwise returns False.
        """

        return self._error_message is not None

    @property
    def is_empty(self):
        """Returns True for BAPI response without any message."""

        return len(self._bapirettab) == 0

    @property
    def error_message(self):
        """Returns the error message if there is any. If the BAPI return value
           does not represent an error, the property holds None.
        """

        return self._error_message


class BAPIError(SAPCliError):
    """RFC BAPI error"""

    def __init__(self, bapireturn: BAPIReturn, response):
        super().__init__(str(bapireturn))

        self.bapiret = bapireturn
        self.response = response

    @staticmethod
    def raise_for_error(bapiret: BAPIReturnRFC, response) -> BAPIReturn:
        """If the given BAPI response contains error raise an exception"""

        bapi_return = BAPIReturn(bapiret)
        if bapi_return.is_error:
            raise BAPIError(bapi_return, response)

        return bapi_return
