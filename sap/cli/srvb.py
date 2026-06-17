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
        # `srvb create` requires --type / --version / --service so the POST
        # carries the binding configuration AND a wired service entry. The
        # server rejects an empty <srvb:services> with PreconditionFailed,
        # so the CLI never offers an "empty binding" mode in v1.
        return sap.adt.ServiceBinding(
            connection, args.name.upper(),
            package=args.package,
            typ=args.binding_type,
            version=args.binding_version,
            service_name=args.service.upper(),
            service_version=args.service_version,
            metadata=metadata,
        )

    def define_create(self, commands):
        create_cmd = super().define_create(commands)
        create_cmd.append_argument('--type', dest='binding_type',
                                   choices=['ODATA', 'INA', 'SQL'], required=True,
                                   help='Service Binding type (srvb:type)')
        create_cmd.append_argument('--version', dest='binding_version',
                                   choices=['V2', 'V4', '1'], required=True,
                                   help='Service Binding version (srvb:version)')
        create_cmd.append_argument('--service', dest='service', required=True,
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
                name = link.definition.name if link.definition else ''
                ver = link.version or ''
                state = link.release_state or ''
                console.printout(f'  {name} (version {ver}, {state})')
