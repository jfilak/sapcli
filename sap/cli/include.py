"""ADT proxy for ABAP Program Include"""

import sap.adt
import sap.cli.object
import sap.cli.core


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

        return sap.adt.Include(connection, name.upper(), master=master, package=package, metadata=metadata)

    def define_activate(self, commands):
        activate_cmd = super().define_activate(commands)
        activate_cmd.append_argument('-m', '--master', nargs='?', default=None, help='Master program')

        return activate_cmd


@CommandGroup.argument('name')
@CommandGroup.command()
def attributes(connection, args):
    """Prints out some attributes of the given include.
    """

    proginc = sap.adt.Include(connection, args.name.upper())
    proginc.fetch()

    console = args.console_factory()

    console.printout(f'Name       : {proginc.name}')
    console.printout(f'Description: {proginc.description}')
    console.printout(f'Responsible: {proginc.responsible}')
    # pylint: disable=no-member
    console.printout(f'Package    : {proginc.reference.name}')

    context = proginc.context
    if context is not None:
        console.printout(f'Main       : {context.name} ({context.typ})')
    else:
        console.printout('Main       :')
