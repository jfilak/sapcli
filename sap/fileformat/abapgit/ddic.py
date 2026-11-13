"""Conversions between ADT and DDIC values shared by the handlers of
   dictionary objects in the abapGit serialization
"""

from sap.platform.abap.ddic import DDIC_DATATYPE_TO_ADT

ADT_TO_DDIC_DATATYPE = {adt: ddic for ddic, adt in DDIC_DATATYPE_TO_ADT.items()}


def ddic_number(value, width):
    """Returns the number formatted as DDIC does or None for 0 because abapGit
       does not write initial values.
    """

    number = int(value or '0')
    return f'{number:0{width}d}' if number else None
