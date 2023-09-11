"""Operations on top of ABAP Structure"""

import sap.adt
import sap.cli.object


class CommandGroup(sap.cli.object.CommandGroupObjectMaster):
    """Adapter converting command line parameters to sap.adt.Structure methods
       calls.
    """

    def __init__(self):
        super().__init__('structure')

        self.define()

    def instance(self, connection, name, args, metadata=None):
        package = getattr(args, 'package', None)

        return sap.adt.Structure(connection, name, package, metadata)
