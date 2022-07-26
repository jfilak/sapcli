"""ADT Proxy for ABAP Table"""

import sap.adt
import sap.cli.object


class CommandGroup(sap.cli.object.CommandGroupObjectMaster):
    """Adapter converting command line parameters to sap.adt.Table methods
       calls.
    """

    def __init__(self):
        super().__init__('table')

        self.define()

    def instance(self, connection, name, args, metadata=None):
        package = getattr(args, 'package', None)

        return sap.adt.Table(connection, name, package, metadata)
