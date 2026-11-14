"""abapGit file format"""

from sap.platform.abap.abapgit.clas import ClassHandler
from sap.platform.abap.abapgit.tabl import TableHandler
from sap.platform.abap.abapgit.dtel import DataElementHandler
from sap.platform.abap.abapgit.doma import DomainHandler
from sap.platform.abap.abapgit.bdef import BehaviorDefinitionHandler
from sap.platform.abap.abapgit.ddlx import MetadataExtensionHandler
from sap.platform.abap.abapgit.dcls import AccessControlHandler
from sap.platform.abap.abapgit.ddls import DataDefinitionHandler
from sap.platform.abap.abapgit.ttyp import TableTypeHandler
from sap.platform.abap.abapgit.fugr import FunctionGroupHandler
from sap.platform.abap.abapgit.intf import InterfaceHandler
from sap.platform.abap.abapgit.prog import ProgramHandler

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
    BehaviorDefinitionHandler(),
    DomainHandler(),
    DataElementHandler(),
    TableHandler(),
)
