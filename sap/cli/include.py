"""ADT proxy for ABAP Program Include"""

import sap.adt
import sap.cli.object


class CommandGroup(sap.cli.object.CommandGroupObjectMaster):
    """Adapter converting command line parameters to sap.adt.Include methods
       calls.
    """

    def __init__(self):
        super().__init__('include')

        self.define()

    def instance(self, connection, name, args, metadata=None):
        master, package = None, None

        if hasattr(args, 'package'):
            package = args.package

        if hasattr(args, 'master'):
            master = args.master

        return sap.adt.Include(connection, name, master=master, package=package, metadata=metadata)

    def define_activate(self, commands):
        activate_cmd = super().define_activate(commands)
        activate_cmd.append_argument('-m', '--master', nargs='?', default=None, help='Master program')

        return activate_cmd
