"""abapGit file format"""

from sap.fileformat.abapgit.clas import ClassHandler
from sap.fileformat.abapgit.ddlx import MetadataExtensionHandler
from sap.fileformat.abapgit.dcls import AccessControlHandler
from sap.fileformat.abapgit.ddls import DataDefinitionHandler
from sap.fileformat.abapgit.ttyp import TableTypeHandler
from sap.fileformat.abapgit.fugr import FunctionGroupHandler
from sap.fileformat.abapgit.intf import InterfaceHandler
from sap.fileformat.abapgit.prog import ProgramHandler

# The single place where object handlers of the abapGit serialization
# are installed.
HANDLERS = (
    ClassHandler(),
    InterfaceHandler(),
    ProgramHandler(),
    FunctionGroupHandler(),
    TableTypeHandler(),
    DataDefinitionHandler(),
    AccessControlHandler(),
    MetadataExtensionHandler(),
)
