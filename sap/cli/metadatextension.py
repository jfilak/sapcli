"""ADT proxy for CDS Metadata Extension (DDLX)"""

import sap.adt
import sap.cli.core
import sap.cli.object


class CommandGroup(sap.cli.object.CommandGroupObjectMaster):
    """Adapter converting command line parameters to sap.adt.MetadataExtension
       methods calls.
    """

    def __init__(self):
        super().__init__('ddlx', description='CDS Metadata Extension')

        self.define()

    def instance(self, connection, name, args, metadata=None):
        package = None
        if hasattr(args, 'package'):
            package = args.package

        return sap.adt.MetadataExtension(connection, name.upper(), package=package, metadata=metadata)
