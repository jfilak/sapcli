"""ADT proxy for ABAP Program (Report)"""

import sap.adt
import sap.cli.object


class CommandGroup(sap.cli.object.CommandGroupObjectMaster):
    """Adapter converting command line parameters to sap.adt.Program methods
       calls.
    """

    def __init__(self):
        super().__init__('program')

        self.define()

    def instance(self, connection, name, args, metadata=None):
        package = None
        if hasattr(args, 'package'):
            package = args.package

        return sap.adt.Program(connection, name, package=package, metadata=metadata)
