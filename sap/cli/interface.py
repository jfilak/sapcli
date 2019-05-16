"""ADT proxy for ABAP Interface (OO)"""

import sap.adt
import sap.cli.object


class CommandGroup(sap.cli.object.CommandGroupObjectMaster):
    """Adapter converting command line parameters to sap.adt.Interface methods
       calls.
    """

    def __init__(self):
        super(CommandGroup, self).__init__('interface')

        self.define()

    def instance(self, connection, name, args, metadata=None):
        package = None
        if hasattr(args, 'package'):
            package = args.package

        return sap.adt.Interface(connection, name, package=package, metadata=metadata)
