"""BAPI helpers and utilities"""

from typing import Union, List

from sap.errors import SAPCliError
from sap.rfc.core import RFCResponse


class BAPIError(SAPCliError):
    """RFC BAPI error"""

    def __init__(self, bapirettab, response):
        super(BAPIError, self).__init__(
            '\n'.join(
                [' '.join([bapiret['TYPE'], bapiret['MESSAGE']]) for bapiret in bapirettab]))

        self.bapirettab = bapirettab
        self.response = response

    @staticmethod
    def raise_for_error(bapiret: Union[RFCResponse, List[RFCResponse]], response) -> None:
        """If the given BAPI response contains error raise an exception"""

        if not isinstance(bapiret, list):
            bapiret = [bapiret]

        if bapiret and any((bapiret['TYPE'] == 'E' for bapiret in bapiret)):
            raise BAPIError(bapiret, response)
