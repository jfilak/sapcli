"""ADT proxy for Behavior Definition (BDEF)"""

import sap.adt
import sap.adt.wb
import sap.cli.core
import sap.cli.object
from sap.errors import SAPCliError
from sap.adt.behaviordefinition import BehaviorDefinition
from sap.adt.common_types import ADTTemplate, ADTTemplateProperty


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

    def define(self):
        commands = super().define()
        if commands is not None:
            self.define_extend(commands)
        return commands

    def define_extend(self, commands):
        """Declares the Extend command with its parameters."""

        extend_cmd = commands.add_command(self.extend_object, name='extend')
        extend_cmd.append_argument('name')
        extend_cmd.append_argument('description')
        extend_cmd.append_argument('package')
        extend_cmd.append_argument('base_bdef', metavar='base-bdef')
        extend_cmd.append_argument('--interface-bdef', default=None,
                                   help='BO Interface to assign the extension to')
        extend_cmd.declare_corrnr()

        return extend_cmd

    def extend_object(self, connection, args):
        """Creates a new behavior extension."""

        base_bdef = args.base_bdef.upper()
        interface_bdef = getattr(args, 'interface_bdef', None)

        if interface_bdef:
            interface_bdef = interface_bdef.upper()
            result = BehaviorDefinition.list_interfaces(connection, base_bdef)
            interface_names = [item.name.lower() for item in result.items]
            if interface_bdef.lower() not in interface_names:
                raise SAPCliError(
                    f'Interface {interface_bdef} is not assigned to behavior definition '
                    f'{base_bdef} or any of its extensions'
                )

        metadata = self.build_new_metadata(connection, args)
        obj = self.build_new_object(connection, args, metadata)
        obj.description = args.description

        obj.template = ADTTemplate([
            ADTTemplateProperty('base_bdef', base_bdef),
            ADTTemplateProperty('interface_bdef', interface_bdef),
        ])

        obj.create(corrnr=args.corrnr)


@CommandGroup.argument('name')
@CommandGroup.command()
def listinterfaces(connection, args):
    """Lists BO interfaces assigned to the given behavior definition"""

    console = args.console_factory()
    result = BehaviorDefinition.list_interfaces(connection, args.name)
    for item in result:
        console.printout(item.name)
