"""ADT proxy for Data Definition (CDS)"""

import sap.adt
import sap.adt.wb
import sap.cli.core
import sap.cli.object


class CommandGroup(sap.cli.object.CommandGroupObjectMaster):
    """Adapter converting command line parameters to sap.adt.DataDefinition
       methods calls.
    """

    def __init__(self):
        super().__init__('ddl', description='CDS views')

        self.define()

    def instance(self, connection, name, args, metadata=None):
        package = None
        if hasattr(args, 'package'):
            package = args.package

        return sap.adt.DataDefinition(connection, name.upper(), package=package, metadata=metadata)
