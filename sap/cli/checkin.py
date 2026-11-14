"""ADT Object import"""
import functools
import os

from sap import get_logger

import sap.errors
import sap.cli.core
import sap.adt
import sap.adt.checks
import sap.adt.objects
import sap.adt.errors
import sap.cli.wb
from sap.config import config_get
from sap.platform.abap.localrepository import CheckinContext
from sap.cli.localrepo import OBJECT_HANDLERS, REPOSITORY_LAYOUT, ConsoleObserver

# The activation group and the position in the group by file types.
# The objects of a group are written in the order of their positions and
# activated together; the groups are processed one after another.
ACTIVATION_ORDER = {
    # Domains go first because other DDIC objects are typed by them
    'doma': (0, 0),
    # Data elements are typed by domains and structures are typed by them
    'dtel': (0, 1),
    # Structures go before table types because table types use them as row types
    'tabl': (0, 2),
    # abapGit deserializes data definitions in the DDIC step too
    'ttyp': (0, 3),
    'ddls': (0, 3),
    # Behavior definitions refer to their behavior pools and behavior
    # pools are classes FOR BEHAVIOR OF behavior definitions, hence they
    # must be activated together but the behavior definitions go first
    'bdef': (1, 0),
    'intf': (1, 1),
    'clas': (1, 1),
    'prog': (2, 0),
    'fugr': (3, 0),
    'dcls': (3, 0),
    'ddlx': (3, 0),
}

ACTIVATION_GROUPS_COUNT = 4


def mod_log():
    """ADT Module logger"""

    return get_logger()


class CommandGroup(sap.cli.core.CommandGroup):
    """Commands for importing ADT objects"""

    def __init__(self):
        super().__init__('checkin')


def checkin_package(connection, package_name, super_package_name, devc, args):
    """Creates the package described by the prepared package file"""

    sap.cli.core.printout(f'Creating Package: {package_name} {devc.CTEXT}')

    metadata = sap.adt.ADTCoreData(language='EN', master_language='EN', responsible=connection.user.upper(),
                                   description=devc.CTEXT)

    package = sap.adt.Package(connection, package_name.upper(), metadata=metadata)
    package.set_package_type('development')

    if super_package_name is not None:
        package.super_package.name = super_package_name.upper()

    package.set_software_component(args.software_component.upper())
    if args.app_component:
        package.set_app_component(args.app_component.upper())

    if args.transport_layer:
        package.set_transport_layer(args.transport_layer.upper())

    try:
        package.create(args.corrnr)
    except sap.adt.errors.ExceptionResourceAlreadyExists as err:
        mod_log().info(err.message)


def _resolve_dependencies(objects):
    """Returns the lists of objects of the activation groups"""

    groups = [[] for _ in range(ACTIVATION_GROUPS_COUNT)]

    # sorted() keeps the order of the objects with the same position
    for obj in sorted(objects, key=lambda obj: ACTIVATION_ORDER[obj.code][1]):
        groups[ACTIVATION_ORDER[obj.code][0]].append(obj)

    return groups


def _prepare_repository(repo, console, observer):
    """Reads and checks the files of all packages and objects before
       accessing the system to avoid long running checkins failing at the end
       because of a file which could not be checked in. Reports all problems
       and returns the prepared data by file paths.
    """

    prepared = {}
    problems = 0

    preparations = [(package.path, functools.partial(REPOSITORY_LAYOUT.prepare_package, package))
                    for package in repo.packages]
    preparations += [(obj.path, functools.partial(obj.handler.prepare, obj, observer)) for obj in repo.objects]

    for path, prepare in preparations:
        try:
            prepared[path] = prepare()
        # InputError (e.g. invalid XML) is not derived from SAPCliError
        except sap.errors.FatalError as ex:
            console.printerr(f'{path}: {ex}')
            problems += 1

    if problems:
        raise sap.errors.SAPCliError(f'Cannot check in {problems} files - nothing has been changed')

    return prepared


# pylint: disable=too-many-arguments,too-many-positional-arguments
def _checkin_dependency_group(connection, group, package_names, used_files, corrnr, check_before_save, prepared,
                              observer):
    """Writes the objects of the activation group, adds the files they
       consumed to used_files and returns the references to activate.
    """

    inactive_objects = sap.adt.objects.ADTObjectReferences()

    for repo_obj in group:
        context = CheckinContext(connection, package_names[repo_obj.package.dir_path], corrnr, check_before_save,
                                 observer)

        # A failure stops the checkin because the objects using the object
        # would fail later anyway
        result = repo_obj.handler.checkin(context, repo_obj, prepared[repo_obj.path])

        for abap_obj in result.abap_objects:
            inactive_objects.add_object(abap_obj)

        used_files.update(result.used_files)

    return inactive_objects


def _activate(connection, inactive_objects, console):
    sap.cli.wb.activate(connection, inactive_objects, console)


def _checkin_repository(connection, args, console, check_before_save):
    observer = ConsoleObserver(console)

    repo = REPOSITORY_LAYOUT.load_repository(args.starting_folder, OBJECT_HANDLERS)
    if repo.starting_folder != args.starting_folder:
        console.printerr(f'Using starting-folder: {repo.starting_folder}')

    package_names = {package.dir_path: REPOSITORY_LAYOUT.package_name(repo, package, args.name)
                     for package in repo.packages}

    console.printout('Checking files ...')
    prepared = _prepare_repository(repo, console, observer)

    console.printout('Creating packages ...')
    for package in repo.packages:
        super_package_name = package_names[package.parent.dir_path] if package.parent is not None else None
        checkin_package(connection, package_names[package.dir_path], super_package_name, prepared[package.path], args)

    used_files = {package.path for package in repo.packages}
    used_files.update(obj.path for obj in repo.objects)

    for activation_group in _resolve_dependencies(repo.objects):
        console.printout('Creating objects ...')
        inactive_objects = _checkin_dependency_group(connection, activation_group, package_names, used_files,
                                                     args.corrnr, check_before_save, prepared, observer)

        if inactive_objects.references:
            console.printout('Activating objects ...')
            _activate(connection, inactive_objects, console)

    for unused_file in sorted(set(repo.files) - used_files):
        console.printerr(f'Unused file: {unused_file}')


@CommandGroup.argument('--no-check', dest='check', action='store_false',
                       help='Skip abapCheckRun before writing source code'
                            ' (overrides SAPCLI_CHECK_BEFORE_SAVE)')
@CommandGroup.argument('--check', dest='check', action='store_true', default=None,
                       help='Run abapCheckRun before writing source code'
                            ' (overrides SAPCLI_CHECK_BEFORE_SAVE)')
@CommandGroup.argument('--starting-folder', default=None)
@CommandGroup.argument('--software-component', type=str, default='LOCAL')
@CommandGroup.argument('--app-component', type=str, default=None)
@CommandGroup.argument('--transport-layer', type=str, default=None)
@CommandGroup.argument('corrnr', type=str, nargs='?', default=None)
@CommandGroup.argument('name', help='Root ABAP package name')
@CommandGroup.command('package')
def do_checkin_directory(connection, args):
    """Synchronize directory structure with ABAP package structure"""

    console = args.console_factory()

    top_dir = '.'
    if args.starting_folder:
        top_dir = os.path.join(top_dir, args.starting_folder)

    if not os.path.isdir(top_dir):
        console.printerr(f'Cannot check-in ABAP objects from "{top_dir}": not a directory')
        return 1

    flag = getattr(args, 'check', None)
    check_before_save = flag if flag is not None else config_get('check_before_save', False)

    try:
        _checkin_repository(connection, args, console, check_before_save)
    except sap.adt.checks.ObjectCheckFindings as findings:
        for line in str(findings).splitlines():
            console.printerr(line)
        return 1
    except sap.errors.SAPCliError as ex:
        console.printerr(f'Checkin failed: {ex}')
        return 1

    return 0
