"""abapGit file format"""

from sap.fileformat.abapgit.clas import ClassHandler
from sap.fileformat.abapgit.intf import InterfaceHandler

# The single place where object handlers of the abapGit serialization
# are installed.
HANDLERS = (
    ClassHandler(),
    InterfaceHandler(),
)
