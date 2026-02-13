"""ADT proxy for Behavior Definition (BDEF)"""

import sap.adt
import sap.adt.wb
import sap.cli.core
import sap.cli.object


class CommandGroup(sap.cli.object.CommandGroupObjectMaster):
    """Adapter converting command line parameters to sap.adt.BehaviorDefinition
       methods calls.
    """

    def __init__(self):
        super().__init__('bdef', description='CDS behavior definition')

        self.define()

    def instance(self, connection, name, args, metadata=None):
        package = None
        if hasattr(args, 'package'):
            package = args.package

        return sap.adt.BehaviorDefinition(connection, name.upper(), package=package, metadata=metadata)
