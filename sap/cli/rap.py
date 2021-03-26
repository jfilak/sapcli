"""
ADT proxy for service binding commands
"""

import sap.adt
import sap.cli.core
import sap.cli.helpers
import sap.cli.wb
import sap.cli.object


class DefinitionGroup(sap.cli.core.CommandGroup):
    """Container for definition commands."""

    def __init__(self):
        super().__init__('definition')


class BindingGroup(sap.cli.core.CommandGroup):
    """Container for binding commands."""

    def __init__(self):
        super().__init__('binding')


class CommandGroup(sap.cli.core.CommandGroup):
    """Commands for rap """

    def __init__(self):
        super().__init__('rap')

        self.definition_grp = DefinitionGroup()
        self.binding_grp = BindingGroup()

    def install_parser(self, arg_parser):
        activation_group = super().install_parser(arg_parser)

        binding_parser = activation_group.add_parser(self.binding_grp.name)
        self.binding_grp.install_parser(binding_parser)

        definition_parser = activation_group.add_parser(self.definition_grp.name)
        self.definition_grp.install_parser(definition_parser)


@BindingGroup.argument('--service', nargs='?', default=None,
                       help='Service name of the binding\'s services to publish')
@BindingGroup.argument('--version', nargs='?', default=None,
                       help='Version of the binding\'s services to publish')
@BindingGroup.argument('binding_name')
@BindingGroup.command()
def publish(connection, args):
    """ publish odata service that belongs to a service binding identified by a version
    """

    console = sap.cli.core.get_console()

    binding = sap.adt.businessservice.ServiceBinding(connection, args.binding_name)
    binding.fetch()

    if not binding.services:
        console.printerr(
            f'Business Service Biding {args.binding_name} does not contain any services')
        return 1

    if args.service is None and args.version is None:
        if len(binding.services) > 1:
            console.printerr(
                f'''Cannot publish Business Service Biding {args.binding_name} without
Service Definition filters because the business binding contains more than one
Service Definition''')
            return 1

        service = binding.services[0]
    else:
        service = binding.find_service(args.service, args.version)
        if service is None:
            console.printerr(
                f'''Business Service Binding {args.binding_name} has no Service Definition
with supplied name "{args.service or ''}" and version "{args.version or ''}"''')
            return 1

    status = binding.publish(service)

    console.printout(status.SHORT_TEXT)
    if status.LONG_TEXT:
        console.printout(status.LONG_TEXT)

    if status.SEVERITY != "OK":
        console.printerr(f'Failed to publish Service {service.definition.name} in Binding {args.binding_name}')
        return 1

    console.printout(
        f'Service {service.definition.name} in Binding {args.binding_name} published successfully.')
    return 0


@DefinitionGroup.argument('name', nargs='+')
@DefinitionGroup.command('activate')
def definition_activate(connection, args):
    """Activate Business Service Definition"""

    activator = sap.cli.wb.ObjectActivationWorker()
    activated_items = ((name, sap.adt.ServiceDefinition(connection, name)) for name in args.name)
    return sap.cli.object.activate_object_list(activator, activated_items, count=len(args.name))
