"""Common ABAP types"""

from sap.platform.abap import Structure, InternalTable


# pylint: disable=invalid-name
# pylint: disable=too-few-public-methods
class DEVC(Structure):
    """Class metadata"""

    # pylint: disable=invalid-name
    CTEXT: str
    SRV_CHECK: str


SUBC_EXECUTABLE_PROGRAM = '1'
SUBC_INCLUDE = 'I'


# pylint: disable=invalid-name
# pylint: disable=too-few-public-methods
# pylint: disable=too-many-instance-attributes
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
    # pylint: disable=invalid-name
    WITH_UNIT_TESTS: str
    CATEGORY: str


# pylint: disable=invalid-name
# pylint: disable=too-few-public-methods
# pylint: disable=too-many-instance-attributes
class VSEOINTERF(Structure):
    """Interface metadata"""

    # pylint: disable=invalid-name
    CLSNAME: str
    # pylint: disable=invalid-name
    VERSION: str
    # pylint: disable=invalid-name
    LANGU: str
    # pylint: disable=invalid-name
    DESCRIPT: str
    # pylint: disable=invalid-name
    EXPOSURE: str
    # pylint: disable=invalid-name
    STATE: str
    # pylint: disable=invalid-name
    UNICODE: str


# pylint: disable=invalid-name
# pylint: disable=too-few-public-methods
# pylint: disable=too-many-instance-attributes
class PROGDIR(Structure):
    """Program metadata"""

    # pylint: disable=invalid-name
    NAME: str
    # pylint: disable=invalid-name
    STATE: str  # A for active; S for saved
    # pylint: disable=invalid-name
    VARCL: str  # X for Case-sensitive
    # pylint: disable=invalid-name
    DBAPL: str  # Application database
    # Program type:
    # 1 Executable program
    # I INCLUDE program
    # M Module Pool
    # F Function group
    # S Subroutine Pool
    # J Interface pool
    # K Class pool
    # T Type Pool
    # X Transformation (XSLT or ST Program)
    # Q Database Procedure Proxy
    # pylint: disable=invalid-name
    SUBC: str
    # pylint: disable=invalid-name
    FIXPT: str  # Fixed point arithmetic
    # pylint: disable=invalid-name
    LDBNAME: str  # LDB name
    # ABAP Version:
    # 2 ABAP for key users
    # 3 Static ABAP with Restricted Object Use
    # 4 Standard ABAP with Restricted Object Use
    # X Standard ABAP (Unicode)
    # ' ' Obsolete ABAP (Not Unicode)
    # pylint: disable=invalid-name
    UCCHECK: str
    RLOAD: str
    RSTAT: str


# pylint: disable=invalid-name
# pylint: disable=too-few-public-methods
# pylint: disable=too-many-instance-attributes
class TPOOL_LINE(Structure):
    """Program texts"""

    # pylint: disable=invalid-name
    ID: str
    # pylint: disable=invalid-name
    ENTRY: str
    # pylint: disable=invalid-name
    LENGTH: str


TPOOL = InternalTable.define('TPOOL', TPOOL_LINE)
