"""ADT proxy for Object Activation routines."""

import sap.adt.object_factory
import sap.cli.core
import sap.errors

from sap.adt.objects import ADTObjectReferences
from sap.adt.wb import fetch_inactive_objects, mass_activate
from sap.cli.core import printout
from sap.cli.helpers import raise_if_object_name_is_not_supported


# ---------------------------------------------------------------------------
# argparse sub-groups
# ---------------------------------------------------------------------------
class InactiveObjectsGroup(sap.cli.core.CommandGroup):
    """Container for inactive objects commands."""

    def __init__(self):
        super().__init__('inactiveobjects')


class ObjectsGroup(sap.cli.core.CommandGroup):
    """Container for explicit object-set commands."""

    def __init__(self):
        super().__init__('objects')


class CommandGroup(sap.cli.core.CommandGroup):
    """Adapter converting command line parameters to sap.adt.wb.* calls."""

    def __init__(self):
        super().__init__('activation')

        self.inactive_objects_grp = InactiveObjectsGroup()
        self.objects_grp = ObjectsGroup()

    def install_parser(self, arg_parser):
        activation_group = super().install_parser(arg_parser)

        inobj_parser = activation_group.add_parser(self.inactive_objects_grp.name)
        self.inactive_objects_grp.install_parser(inobj_parser)

        obj_parser = activation_group.add_parser(self.objects_grp.name)
        self.objects_grp.install_parser(obj_parser)


# ---------------------------------------------------------------------------
# Helpers shared by all commands in this module
# ---------------------------------------------------------------------------
def _print_entry(entry, prefix=''):
    """Pretty-print a single inactive-objects entry."""

    printout(f'{prefix}{entry.object.name} ({entry.object.typ})')


def _walk_inactive(inactive_results, callback):
    """Iterate inactive_results.entries with parent-then-child ordering.

    Mirrors the structure already used by ``inactiveobjects list`` so
    that output and reference collection share the same traversal.
    """

    handled = set()

    for root_entry in inactive_results.entries:
        if root_entry.object is None:
            continue
        if root_entry.object.parent_uri:
            continue

        root_uri = root_entry.object.uri
        if root_uri in handled:
            continue

        callback(root_entry, '')
        handled.add(root_uri)

        for child_entry in inactive_results.entries:
            if child_entry.object is None:
                continue
            if root_uri != child_entry.object.parent_uri:
                continue

            child_uri = child_entry.object.uri
            if child_uri in handled:
                continue

            handled.add(child_uri)
            callback(child_entry, ' + ')

    for leftover_entry in inactive_results.entries:
        if leftover_entry.object is None:
            continue

        leftover_uri = leftover_entry.object.uri
        if leftover_uri in handled:
            continue

        callback(leftover_entry, '')


def _report_results(results, ignore_errors, warning_errors):
    """Print activation messages and return an exit code (0 ok, 1 fail)."""

    if results.has_errors or (results.has_warnings and warning_errors):
        if results.has_errors:
            printout('Activation reported errors:')
        else:
            printout('Activation reported warnings (treated as errors):')

        for message in results.messages:
            printout(f'  {message.typ} {message.obj_descr}: {message.short_text}')

        if not ignore_errors:
            return 1
    elif results.has_warnings:
        printout('Activation reported warnings:')
        for message in results.messages:
            if message.is_warning:
                printout(f'  W {message.obj_descr}: {message.short_text}')

    printout('Activation finished.')
    return 0


def _parse_object_spec(spec, supported_kinds):
    """Parse a ``KIND=NAME`` argument value into ``(kind, name)``."""

    if '=' not in spec:
        raise sap.errors.SAPCliError(
            f"Invalid --object value '{spec}'. Expected KIND=NAME.")

    kind, name = spec.split('=', 1)
    kind = kind.strip().lower()
    name = name.strip()

    if not kind or not name:
        raise sap.errors.SAPCliError(
            f"Invalid --object value '{spec}'. Both KIND and NAME must be non-empty.")

    raise_if_object_name_is_not_supported(kind, supported_kinds)

    return kind, name


# ---------------------------------------------------------------------------
# Commands: activation inactiveobjects ...
# ---------------------------------------------------------------------------
@InactiveObjectsGroup.command('list')
# pylint: disable=unused-argument
def inactiveobjects_list(connection, args):
    """Print out all inactive objects"""

    inactive_results = fetch_inactive_objects(connection)
    _walk_inactive(inactive_results, _print_entry)


@InactiveObjectsGroup.argument('--dry-run', '-n', action='store_true', default=False,
                               help='List the objects that would be activated, then exit')
@InactiveObjectsGroup.argument('--warning-errors', action='store_true', default=False,
                               help='Treat activation warnings as errors')
@InactiveObjectsGroup.argument('--ignore-errors', action='store_true', default=False,
                               help='Return success even if activation reports errors')
@InactiveObjectsGroup.command('activate')
def inactiveobjects_activate(connection, args):
    """Activate everything in the user's inactive worklist in one ADT request.

    Submits the entire worklist as one ADT activation request, so
    cross-references between currently-inactive siblings are resolved
    by the kernel in a single transaction.
    """

    inactive_results = fetch_inactive_objects(connection)

    refs = ADTObjectReferences()
    seen_uris = set()

    def collect(entry, _prefix):
        if entry.object is None:
            return
        if entry.object.deleted == 'true':
            return
        ref = entry.object.reference
        if not ref.uri or ref.uri in seen_uris:
            return
        seen_uris.add(ref.uri)
        refs.references.append(ref)

    _walk_inactive(inactive_results, collect)

    if not refs.references:
        printout('No inactive objects.')
        return 0

    printout(f'Activating {len(refs.references)} object(s):')
    for ref in refs.references:
        printout(f'  {ref.name} ({ref.typ})')

    if args.dry_run:
        printout('Dry run - nothing was sent to the server.')
        return 0

    results, _resp = mass_activate(connection, refs)
    return _report_results(results, args.ignore_errors, args.warning_errors)


# ---------------------------------------------------------------------------
# Commands: activation objects ...
# ---------------------------------------------------------------------------
@ObjectsGroup.argument('--dry-run', '-n', action='store_true', default=False,
                       help='List the objects that would be activated, then exit')
@ObjectsGroup.argument('--warning-errors', action='store_true', default=False,
                       help='Treat activation warnings as errors')
@ObjectsGroup.argument('--ignore-errors', action='store_true', default=False,
                       help='Return success even if activation reports errors')
@ObjectsGroup.argument('--object', dest='objects', action='append',
                       metavar='KIND=NAME',
                       help='Add an object to the bundle (repeat for multiple). '
                            'Examples: --object program=YOUR_PROGRAM '
                            '--object include=YOUR_INCLUDE. '
                            'Run with --list-kinds to see all supported KINDs.')
@ObjectsGroup.argument('--list-kinds', action='store_true', default=False,
                       help='Print the list of supported KINDs and exit')
@ObjectsGroup.command('activate')
def objects_activate(connection, args):
    """Bundle-activate a specific set of named objects in one ADT request.

    Use repeated ``--object KIND=NAME`` flags to enumerate the bundle.
    Like ``inactiveobjects activate``, the kernel resolves cross-references
    in a single transaction so cross-referencing inactive objects are
    activated together.
    """

    if args.list_kinds:
        # Render kinds without a live connection - the factory only
        # needs one for actually building objects, so we pass None and
        # only consult the supported-names list.
        factory = sap.adt.object_factory.human_names_factory(None)
        printout('Supported KINDs:')
        for kind in sorted(factory.get_supported_names()):
            printout(f'  {kind}')
        return 0

    if not args.objects:
        raise sap.errors.SAPCliError(
            'At least one --object KIND=NAME is required unless --list-kinds is used.')

    factory = sap.adt.object_factory.human_names_factory(connection)
    supported_kinds = list(factory.get_supported_names())

    refs = ADTObjectReferences()
    summary = []   # list of (kind, name) for printout/dry-run

    for spec in args.objects:
        kind, name = _parse_object_spec(spec, supported_kinds)
        obj = factory.make(kind, name)
        refs.add_object(obj)
        summary.append((kind, name))

    printout(f'Activating {len(summary)} object(s):')
    for kind, name in summary:
        printout(f'  {kind} {name}')

    if args.dry_run:
        printout('Dry run - nothing was sent to the server.')
        return 0

    results, _resp = mass_activate(connection, refs)
    return _report_results(results, args.ignore_errors, args.warning_errors)
