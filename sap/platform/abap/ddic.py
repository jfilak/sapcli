"""Common ABAP types"""

from typing import Any  # noqa: F401
from sap.platform.abap import Structure, InternalTable, ItemizedTable


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
# pylint: disable=invalid-name
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
    EXPOSURE: str
    CLSFINAL: str
    CLSABSTRCT: str
    # pylint: disable=invalid-name
    DURATION_TYPE: str
    # pylint: disable=invalid-name
    RISK_LEVEL: str


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
    DBNA: str
    APPL: str


# pylint: disable=too-few-public-methods
# pylint: disable=too-many-instance-attributes
# pylint: disable=invalid-name
class TPOOL_LINE(Structure):
    """Program texts"""

    # pylint: disable=invalid-name
    ID: str
    # pylint: disable=invalid-name
    ENTRY: str
    # pylint: disable=invalid-name
    LENGTH: str


TPOOL = ItemizedTable.define('TPOOL', TPOOL_LINE)

# Function group
AREAT = type('AREAT', (str,), {})
INCLUDES = InternalTable.define('INCLUDES', str)


class RSIMP(Structure):
    """Import metadata"""

    PARAMETER: str
    DEFAULT: str
    OPTIONAL: str
    REFERENCE: str
    TYP: str


IMPORT_TYPE = InternalTable.define('IMPORT', RSIMP)  # type: Any


class RSCHA(Structure):
    """Changing metadata"""

    PARAMETER: str
    DEFAULT: str
    OPTIONAL: str
    REFERENCE: str
    TYP: str


CHANGING_TYPE = InternalTable.define('CHANGING', RSCHA)  # type: Any


class RSEXP(Structure):
    """Export metadata"""

    PARAMETER: str
    REFERENCE: str
    TYP: str


EXPORT_TYPE = InternalTable.define('EXPORT', RSEXP)  # type: Any


class RSTBL(Structure):
    """Table metadata"""

    PARAMETER: str
    OPTIONAL: str
    DBSTRUCT: str


TABLE_TYPE = InternalTable.define('TABLES', RSTBL)  # type: Any


class RSEXC(Structure):
    """Exception metadata"""

    EXCEPTION: str


EXCEPTION_TYPE = InternalTable.define('EXCEPTION', RSEXC)  # type: Any


class RSFDO(Structure):
    """Documentation metadata"""

    PARAMETER: str
    KIND: str


DOCUMENTATION_TYPE = InternalTable.define('DOCUMENTATION', RSFDO)  # type: Any


class FUNCTION_LINE(Structure):
    """Function metadata"""

    FUNCNAME: str
    REMOTE_CALL: str
    SHORT_TEXT: str
    IMPORT: IMPORT_TYPE
    CHANGING: CHANGING_TYPE
    EXPORT: EXPORT_TYPE
    TABLES: TABLE_TYPE
    EXCEPTION: EXCEPTION_TYPE
    DOCUMENTATION: DOCUMENTATION_TYPE


FUNCTIONS = ItemizedTable.define('FUNCTIONS', FUNCTION_LINE)


# CUA (Common User Access) types

class RSMPE_ADM(Structure):
    """CUA administration"""

    PFKCODE: str


class RSMPE_STAT(Structure):
    """CUA status definition"""

    CODE: str
    MODAL: str
    PFKCODE: str
    BUTCODE: str
    INT_NOTE: str


class RSMPE_FUNT(Structure):
    """CUA function definition"""

    CODE: str
    TEXTNO: str
    TYPE: str
    TEXT_TYPE: str
    TEXT_NAME: str
    ICON_ID: str
    FUN_TEXT: str
    ICON_TEXT: str
    PATH: str


class RSMPE_BUT(Structure):
    """CUA button mapping"""

    PFK_CODE: str
    CODE: str
    NO: str
    PFNO: str


class RSMPE_PFK(Structure):
    """CUA PF key mapping"""

    CODE: str
    PFNO: str
    FUNCODE: str
    FUNNO: str


class RSMPE_STAF(Structure):
    """CUA status-function association"""

    STATUS: str
    FUNCTION: str


class RSMPE_ATRT(Structure):
    """CUA attributes"""

    OBJ_TYPE: str
    OBJ_CODE: str
    SUB_CODE: str
    MODAL: str
    INT_NOTE: str


STA_TYPE = InternalTable.define('STA', RSMPE_STAT)  # type: Any
FUN_TYPE = InternalTable.define('FUN', RSMPE_FUNT)  # type: Any
BUT_TYPE = InternalTable.define('BUT', RSMPE_BUT)  # type: Any
PFK_TYPE = InternalTable.define('PFK', RSMPE_PFK)  # type: Any
SET_TYPE = InternalTable.define('SET', RSMPE_STAF)  # type: Any
DOC_TYPE = InternalTable.define('DOC', RSMPE_ATRT)  # type: Any


class CUA(Structure):
    """CUA (Common User Access) definition"""

    ADM: RSMPE_ADM
    STA: STA_TYPE
    FUN: FUN_TYPE
    BUT: BUT_TYPE
    PFK: PFK_TYPE
    SET: SET_TYPE
    DOC: DOC_TYPE
