"""Common ABAP types"""

from sap.platform.abap import Structure


# pylint: disable=invalid-name
# pylint: disable=too-few-public-methods
class VSEOCLASS(Structure):
    """Class metadata"""

    # pylint: disable=invalid-name
    CLSNAME: str
    # pylint: disable=invalid-name
    VERSION: str
    # pylint: disable=invalid-name
    LANGU: str
    # pylint: disable=invalid-name
    DESCRIPT: str
    # pylint: disable=invalid-name
    STATE: str
    # pylint: disable=invalid-name
    CLSCCINCL: str
    # pylint: disable=invalid-name
    FIXPT: str
    # pylint: disable=invalid-name
    UNICODE: str
