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


def adt_flag_to_abap(value):
    """Returns ABAP flag of the given ADT boolean value or None for false
       because abapGit does not write initial values.
    """

    return 'X' if value == 'true' else None


def abap_flag_to_adt(flag):
    """Returns ADT boolean value of the given ABAP flag"""

    return 'true' if flag else 'false'
