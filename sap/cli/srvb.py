"""ADT proxy for Service Binding (SRVB)"""

import json
import urllib.parse
import webbrowser
import sap.errors
import sap.adt
import sap.cli.object
import sap.cli.wb
import sap.rest.connection


class CommandGroupPreview(sap.cli.core.CommandGroup):
    """Adapter converting command line parameters to sap.adt.ServiceBinding
       methods calls.
    """

    def __init__(self):
        super().__init__('preview', description='Preview utilities for Service Binding (SRVB)')


class CommandGroup(sap.cli.object.CommandGroupObjectMaster):
    """Adapter converting command line parameters to sap.adt.ServiceBinding
       methods calls.
    """

    def __init__(self):
        super().__init__('srvb', description='Service Binding (SRVB)')

        self.command_group_preview = CommandGroupPreview()

        self.define()

    def install_parser(self, arg_parser):
        super_parser = super().install_parser(arg_parser)

        child_parser = super_parser.add_parser(self.command_group_preview.name)
        self.command_group_preview.install_parser(child_parser)

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
                    console.printout('    Entity Sets and Associations:')
                    for info in service_group.services.service_information.collection:
                        console.printout(f'      {info.name}')


def _print_service_line(console, action, service):
    """Prints the operation header and the affected service in the form:

           <action>:
           * <Service Definition> <Service Name> <Service Version>
    """

    console.printout(f'{action}:')
    console.printout('*', service.definition.name, service.name, service.version)


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

    _print_service_line(console, 'Publishing', service)

    status = binding.publish(service)

    console.printout(status.SHORT_TEXT)
    if status.LONG_TEXT:
        console.printout(status.LONG_TEXT)

    if status.SEVERITY != 'OK':
        console.printerr(
            f'Failed to publish Service {service.definition.name} in Binding {args.binding_name}')
        return 1

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


def _activate_binding(binding, args, console):
    """Activates the given Service Binding using the standard activation
       reporting and returns its exit code (0 on success, 1 on errors).
    """

    activator = sap.cli.wb.ObjectActivationWorker()
    activator.continue_on_errors = args.ignore_errors
    activator.warnings_as_errors = args.warning_errors

    return sap.cli.object.activate_object_list(activator, [(binding.name, binding)], 1, console)


@CommandGroup.argument('--warning-errors', action='store_true', default=False,
                       help='Treat activation warnings as errors (only with --activate)')
@CommandGroup.argument('--ignore-errors', action='store_true', default=False,
                       help='Do not stop activation in case of errors (only with --activate)')
@CommandGroup.argument('-a', '--activate', action='store_true', default=False,
                       help='Activate the Service Binding after successful unpublishing')
@CommandGroup.argument('--version', nargs='?', default=None,
                       help="Version of the binding's services to unpublish")
@CommandGroup.argument('--service', nargs='?', default=None,
                       help="Service name of the binding's services to unpublish")
@CommandGroup.argument('binding_name')
@CommandGroup.command('unpublish')
def unpublish(connection, args):
    """Unpublish odata/ina/sql service that belongs to a service binding.

    Logic mirrors the `publish` handler verbatim — when the binding contains
    exactly one service, omitting `--service`/`--version` unpublishes that one;
    otherwise the two filters narrow which content entry is selected.

    When `--activate` is given, the binding is activated after a successful
    unpublish.
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
                f'''Cannot unpublish Business Service Biding {args.binding_name} without
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

    _print_service_line(console, 'Unpublishing', service)

    status = binding.unpublish(service)

    console.printout(status.SHORT_TEXT)
    if status.LONG_TEXT:
        console.printout(status.LONG_TEXT)

    if status.SEVERITY != 'OK':
        console.printerr(
            f'Failed to unpublish Service {service.definition.name} in Binding {args.binding_name}')
        return 1

    if args.activate:
        return _activate_binding(binding, args, console)

    return 0


def _get_service_with_binding_group(connection, args):

    binding = sap.adt.ServiceBinding(connection, args.binding_name.upper())
    binding.fetch()

    if not binding.services:
        raise sap.errors.SAPCliError(f'Business Service Biding {args.binding_name} does not contain any services')

    if len(binding.services) > 1 and args.service is None:
        raise sap.errors.SAPCliError(
            f'Business Service Biding {args.binding_name} contains more than one Service Definition; '
            'use --service to specify which one to preview')

    if args.service is not None:
        for link in binding.services:
            name = link.name
            if name == args.service:
                break
        else:
            raise sap.errors.SAPCliError(
                f'Business Service Biding {args.binding_name} has no Service Definition '
                f'with supplied name "{args.service}"')
    else:
        # pylint: disable=unsubscriptable-object
        link = binding.services[0]

    service_group = binding.get_service_group(link)
    if service_group is None:
        raise sap.errors.SAPCliError(
            f'Failed to retrieve service group for Service Definition {link.name} in '
            f'Binding {args.binding_name}')

    return binding, service_group


@CommandGroupPreview.argument('--service', nargs='?', default=None,
                              help="Service name of the binding's services to preview")
@CommandGroupPreview.argument('binding_name')
@CommandGroupPreview.command('metadata')
def preview_metadata(connection, args):
    """Download and print the OData metadata document for one of the services in a Service Binding."""

    console = args.console_factory()
    _, service_group = _get_service_with_binding_group(connection, args)
    metadata = connection.execute('GET', service_group.services.service_url + '/$metadata', complete_url=True).text
    console.printout(metadata)


@CommandGroupPreview.argument('--service', nargs='?', default=None,
                              help="Service name of the binding's services to preview")
@CommandGroupPreview.argument('entity_set')
@CommandGroupPreview.argument('binding_name')
@CommandGroupPreview.command('fetch')
def preview_fetch(connection, args):
    """Fetch and print entries from the specified entity set of one of the services in a Service Binding."""

    console = args.console_factory()
    _, service_group = _get_service_with_binding_group(connection, args)
    data = connection.execute(
        'GET',
        service_group.services.service_url + '/' + args.entity_set,
        accept='application/json',
        complete_url=True
    ).json()

    console.printout(json.dumps(data, indent=2))


def _encode_feap_path_params(service_url, entity_set, service_name, service_version, group_name):
    """Encode the seven-component path fragment expected by the `feap/.../flp.html`
       Fiori launchpad preview endpoint.

       The encoding recipe is the one used by ADT's own web frontend: components
       are joined by ``##``, every character's code point is shifted by +20 and
       the resulting string is URL-quoted.
    """

    components = [service_url, entity_set, '', '', service_name, service_version, group_name]
    params = "##".join(components)
    encodedparams = "".join([chr(b) for b in [ord(c) + 20 for c in params]])
    return urllib.parse.quote(encodedparams)


@CommandGroupPreview.argument('--open', dest='open_in_browser', action='store_true', default=False,
                              help='Open the preview page in the default web browser instead of '
                                   'downloading it')
@CommandGroupPreview.argument('--service', nargs='?', default=None,
                              help="Service name of the binding's services to preview")
@CommandGroupPreview.argument('entity_set')
@CommandGroupPreview.argument('binding_name')
@CommandGroupPreview.command('html')
def preview_html(connection, args):
    """Fetch and print the Fiori launchpad preview HTML page for the given
       entity set of one of the services in a Service Binding.

       With ``--open``, the URL of the preview page is opened in the user's
       default web browser using Python's OS-agnostic ``webbrowser`` module
       instead of being downloaded.
    """

    console = args.console_factory()
    _, service_group = _get_service_with_binding_group(connection, args)

    if not isinstance(service_group, sap.adt.businessservice.ODataV4ServiceGroup):
        raise sap.errors.SAPCliError(
            'sapcli srvb preview html is currently supported only for OData V4 Service Bindings')

    service = service_group.services
    encoded_path_params = _encode_feap_path_params(
        service.service_url,
        args.entity_set,
        service.service_information.service_name,
        service.service_information.service_version,
        service_group.name,
    )

    # `connection._http_client.client` is the only place where the SAP client
    # currently exposed on the ADT Connection lives; the corresponding public
    # accessor does not exist yet, so reach into the HTTP client directly.
    # pylint: disable=protected-access
    sap_client = connection._http_client.client

    query_params = {
        'sap-ui-xx-viewCache': 'false',
        'sap-ui-language': 'EN',
        'sap-client': sap_client,
    }
    path = f'businessservices/odatav4/feap/{encoded_path_params}/flp.html'

    if args.open_in_browser:
        # pylint: disable=protected-access
        base_url = connection._http_client._base_url
        query_string = urllib.parse.urlencode(query_params)
        full_url = f'{base_url}/sap/bc/adt/{path}?{query_string}#app-preview'
        webbrowser.open(full_url)
        return

    html = connection.execute('GET', path, params=query_params).text
    console.printout(html)
