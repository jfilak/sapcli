"""ADT proxy for Service Definition (SRVD)"""

import sap.adt
import sap.adt.businessservice
import sap.cli.apirelease
import sap.cli.object


class CommandGroup(sap.cli.object.CommandGroupObjectMaster):
    """Adapter converting command line parameters to sap.adt.ServiceDefinition
       methods calls.
    """

    def __init__(self):
        super().__init__('srvd', description='Service Definition (SRVD)')

        self.define()
        sap.cli.apirelease.enhance_command_group(self)

    def define_create(self, commands):
        create_cmd = super().define_create(commands)

        create_cmd.append_argument(
            '--type',
            choices=[source_type.name.lower() for source_type in sap.adt.businessservice.SourceType],
            default=sap.adt.businessservice.SourceType.DEFINITION.name.lower(),
            help='Service definition source type (default: definition)')

        return create_cmd

    def instance(self, connection, name, args, metadata=None):
        package = None
        if hasattr(args, 'package'):
            package = args.package

        kwargs = {'package': package, 'metadata': metadata}
        if hasattr(args, 'type'):
            kwargs['source_type'] = sap.adt.businessservice.SourceType[args.type.upper()]

        return sap.adt.ServiceDefinition(connection, name.upper(), **kwargs)
