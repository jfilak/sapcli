"""ADT proxy for Service Binding (SRVB)"""

import sap.adt
import sap.cli.object


class CommandGroup(sap.cli.object.CommandGroupObjectMaster):
    """Adapter converting command line parameters to sap.adt.ServiceBinding
       methods calls.
    """

    def __init__(self):
        super().__init__('srvb', description='Service Binding (SRVB)')

        self.define()

    def instance(self, connection, name, args, metadata=None):
        package = None
        if hasattr(args, 'package'):
            package = args.package

        return sap.adt.ServiceBinding(connection, name.upper(), package=package, metadata=metadata)

    def build_new_object(self, connection, args, metadata):
        # `srvb create` requires --binding-type and --service-definition

        # We can validate by:
        #   GET /sap/bc/adt/businessservices/bindings/bindingtypes HTTP/1.1
        #   Accept: application/vnd.sap.adt.nameditems.v1+xml, application/xml
        typ, version, category = {
            'ODATAV2_UI': ('ODATA', 'V2', '0'),
            'ODATAV2_API': ('ODATA', 'V2', '1'),
            'ODATAV4_UI': ('ODATA', 'V4', '0'),
            'ODATAV4_API': ('ODATA', 'V4', '1'),
        }.get(args.binding_type, (None, None, None))

        binding = sap.adt.ServiceBinding(
            connection, args.name.upper(),
            package=args.package,
            typ=typ,
            version=version,
            category=category,
            metadata=metadata,
        )

        # The SRVB API requires at least one service to be present on creation
        # Args: new service name, service definition, and new service version
        binding.add_service(args.name.upper(), args.service_definition.upper(), args.service_version)

        return binding

    def define_create(self, commands):
        create_cmd = super().define_create(commands)
        create_cmd.append_argument('--binding-type', dest='binding_type',
                                   choices=[
                                       'ODATAV2_UI',
                                       'ODATAV2_API',
                                       'ODATAV4_UI',
                                       'ODATAV4_API',
                                   ],
                                   required=True,
                                   help='Service Binding type')
        create_cmd.append_argument('--service-definition', dest='service_definition', required=True,
                                   help='Name of the Service Definition (SRVD) to wire into the binding')
        create_cmd.append_argument('--service-version', dest='service_version', default='0001',
                                   help='Version of the wired Service Definition (default: 0001)')
        return create_cmd

    def define_write(self, commands):
        # No `srvb write` in v1: SRVB has no text/plain source body, so the
        # default plain-text editor would not work. v2 will replace this with
        # a JSON round-trip implementation; explicit None disables the
        # write subcommand for now.
        return None

    def read_object_text(self, connection, args):
        # Override the default `obj.text` printer because Service Bindings
        # have no source body. Print a structural summary instead.
        console = args.console_factory()

        binding = self.instance(connection, args.name, args)
        binding.fetch()

        # `binding.reference` always exists (it's the embedded packageRef
        # object); only `.name` is populated by fetch(). The inner
        # `binding.binding` and `binding.services` may be unset on edge cases
        # so guard them with `if`.
        package = binding.reference.name or ''
        typ = binding.binding.typ if binding.binding else ''
        version = binding.binding.version if binding.binding else ''

        console.printout(f'Name        : {binding.name}')
        console.printout(f'Description : {binding.description or ""}')
        console.printout(f'Package     : {package}')
        console.printout(f'Type        : {typ}')
        console.printout(f'Version     : {version}')
        console.printout(f'Published   : {binding.published or "false"}')

        if binding.services:
            console.printout('Services:')
            # pylint: disable=not-an-iterable

            for link in binding.services:
                name = link.name
                ver = link.version or ''
                state = link.release_state or ''
                console.printout(f'  {name} (version {ver}, {state})')
                service_group = binding.get_service_group(link)
                if service_group:
                    console.printout(f'    URL: {service_group.services.service_url}')


def publish_binding(connection, args):
    """Publish a Service Binding's service to its local endpoint.

    Logic mirrors the legacy `sap.cli.rap.publish` handler verbatim — when
    the binding contains exactly one service, omitting `--service`/`--version`
    publishes that one; otherwise the two filters narrow which content entry
    is selected.
    """

    console = args.console_factory()

    binding = sap.adt.ServiceBinding(connection, args.binding_name)
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

        # pylint: disable=unsubscriptable-object
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

    if status.SEVERITY != 'OK':
        console.printerr(
            f'Failed to publish Service {service.definition.name} in Binding {args.binding_name}')
        return 1

    console.printout(
        f'Service {service.definition.name} in Binding {args.binding_name} published successfully.')
    return 0


# Hook `publish` into the `srvb` command group via the class-level decorators.
# The decorator runs at module load time and registers the command into
# CommandGroup.commands; the order with respect to define() in __init__
# is irrelevant because both feed into the same class-level CommandsList.
@CommandGroup.argument('--version', nargs='?', default=None,
                       help="Version of the binding's services to publish")
@CommandGroup.argument('--service', nargs='?', default=None,
                       help="Service name of the binding's services to publish")
@CommandGroup.argument('binding_name')
@CommandGroup.command('publish')
def publish(connection, args):
    """Publish odata/ina/sql service that belongs to a service binding."""

    return publish_binding(connection, args)
