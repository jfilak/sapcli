"""ADT proxy for Access Control (DCL)"""

import sap.adt
import sap.adt.wb
import sap.cli.core
import sap.cli.object


class CommandGroup(sap.cli.object.CommandGroupObjectMaster):
    """Adapter converting command line parameters to sap.adt.AccessControl
       methods calls.
    """

    def __init__(self):
        super().__init__('dcl', description='CDS access control')

        self.define()

    def instance(self, connection, name, args, metadata=None):
        package = None
        if hasattr(args, 'package'):
            package = args.package

        return sap.adt.AccessControl(connection, name.upper(), package=package, metadata=metadata)
