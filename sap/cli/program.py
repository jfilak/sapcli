"""ADT proxy for ABAP Program (Report)"""

import sap.adt
import sap.adt.textelements
import sap.adt.wb
import sap.cli.object
import sap.cli.wb


SOURCE_TYPES = ['main', 'textelements']


class ProgramActivationWorker(sap.cli.wb.ObjectActivationWorker):
    """Activates Programs together with their Text Elements because ADT
       does not activate inactive Text Elements with the Program.
    """

    def activate_object(self, obj):
        if not isinstance(obj, sap.adt.Program):
            return super().activate_object(obj)

        text_elements = sap.adt.textelements.ProgramTextElements(obj.connection, obj.name)
        return sap.adt.wb.try_activate(obj, dependents=[text_elements])


class CommandGroup(sap.cli.object.CommandGroupObjectMaster):
    """Adapter converting command line parameters to sap.adt.Program methods
       calls.
    """

    def __init__(self):
        super().__init__('program')

        self.define()

    def instance(self, connection, name, args, metadata=None):
        if getattr(args, 'type', None) == 'textelements':
            return sap.adt.textelements.ProgramTextElements(connection, name.upper())

        package = None
        if hasattr(args, 'package'):
            package = args.package

        return sap.adt.Program(connection, name.upper(), package=package, metadata=metadata)

    def build_activator(self, args):
        activator = ProgramActivationWorker()

        activator.continue_on_errors = args.ignore_errors
        activator.warnings_as_errors = args.warning_errors

        return activator

    def define_read(self, commands):
        read_cmd = super().define_read(commands)
        read_cmd.insert_argument(1, '--type', default=SOURCE_TYPES[0], choices=SOURCE_TYPES)

        return read_cmd

    def define_write(self, commands):
        write_cmd = super().define_write(commands)
        write_cmd.insert_argument(1, '--type', default=SOURCE_TYPES[0], choices=SOURCE_TYPES)

        return write_cmd


@CommandGroup.argument('name')
@CommandGroup.command()
def execute(connection, args):
    """Runs the executable program and prints its output"""

    program = sap.adt.Program(connection, args.name.upper())
    print(program.execute())
