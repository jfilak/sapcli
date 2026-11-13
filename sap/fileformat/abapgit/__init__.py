"""abapGit file format"""

from sap.fileformat.abapgit.clas import ClassHandler

# The single place where object handlers of the abapGit serialization
# are installed.
HANDLERS = (
    ClassHandler(),
)
