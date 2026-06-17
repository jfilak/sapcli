"""ADT proxy for Service Definition (SRVD)"""

import sap.adt
import sap.cli.object


class CommandGroup(sap.cli.object.CommandGroupObjectMaster):
    """Adapter converting command line parameters to sap.adt.ServiceDefinition
       methods calls.
    """

    def __init__(self):
        super().__init__('srvd', description='Service Definition (SRVD)')

        self.define()

    def instance(self, connection, name, args, metadata=None):
        package = None
        if hasattr(args, 'package'):
            package = args.package

        return sap.adt.ServiceDefinition(connection, name.upper(), package=package, metadata=metadata)
