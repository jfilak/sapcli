# pylint: disable=too-many-lines
"""ADT Object import"""
import os
import glob
import errno
import typing

from sap import get_logger

import sap.errors
import sap.cli.core
import sap.platform.abap.abapgit
from sap.platform.abap.ddic import DEVC
import sap.adt
import sap.adt.checks
import sap.adt.objects
import sap.adt.errors
import sap.adt.textelements
import sap.adt.wb
import sap.cli.wb
from sap.config import config_get
import sap.fileformat.adt
import sap.fileformat.abapgit
from sap.fileformat import HandlerRegistry, CheckinContext

# Handlers of the object types already migrated to sap.fileformat
OBJECT_HANDLERS = HandlerRegistry(sap.fileformat.abapgit.HANDLERS)


def mod_log():
    """ADT Module logger"""

    return get_logger()


class CommandGroup(sap.cli.core.CommandGroup):
    """Commands for importing ADT objects"""

    def __init__(self):
        super().__init__('checkin')


class RepoPackage(typing.NamedTuple):
    """Package on file system"""

    name: str
    path: str
    dir_path: str
    parent: typing.Any


class RepoObject(typing.NamedTuple):
    """ADT object of Repository"""

    code: str
    name: str
    path: str
    package: RepoPackage
    files: list


# pylint: disable=too-many-instance-attributes
class Repository:
    """Repository information"""

    def __init__(self, name, config):
        self._name = name
        self._full_fmt = '$%s' if name[0] == '$' else '%s'
        self._pfx_fmt = f'{name}_%s'
        self._config = config

        self._dir_prefix = config.STARTING_FOLDER.split('/')
        if not self._dir_prefix[0]:
            del self._dir_prefix[0]

        if not self._dir_prefix[-1]:
            del self._dir_prefix[-1]

        self._packages = {}
        self._objects = []
        self._files = set()
        self._used_files = set()

        self._pkg_name_bldr = {
            sap.platform.abap.abapgit.FOLDER_LOGIC_FULL: lambda parts: self._full_fmt % (parts[-1]),
            # pylint: disable=unnecessary-lambda
            sap.platform.abap.abapgit.FOLDER_LOGIC_PREFIX: lambda parts: self._pfx_fmt % ('_'.join(parts)),
        }[config.FOLDER_LOGIC]

    @property
    def config(self):
        """Get config"""

        return self._config

    @property
    def packages(self):
        """List of packages"""

        return list(self._packages.values())

    @property
    def objects(self):
        """List of packages"""

        return self._objects

    @property
    def unused_files(self):
        """Sorted list of recorded files which were not marked as used"""

        return sorted(self._files - self._used_files)

    def find_package_by_path(self, dir_path):
        """Get package based on its path"""

        return self._packages[dir_path]

    def add_file(self, file_path):
        """Record a file found in the repository directory structure"""

        self._files.add(file_path)

    def mark_file_used(self, file_path):
        """Mark the given repository file as consumed by checkin"""

        self._used_files.add(file_path)

    def add_object(self, obj_file_name, package):
        """Add new ADT object"""

        obj_id_start = obj_file_name.find('.') + 1

        if obj_id_start + 4 > len(obj_file_name) - 4:
            raise sap.errors.SAPCliError(f'Invalid ABAP file name: {obj_file_name}')

        obj_code = obj_file_name[obj_id_start:(obj_id_start + 4)]
        mod_log().debug('Handling object code: %s (%s)', obj_code, obj_file_name)

        obj_name = obj_file_name[:obj_id_start - 1]

        other_files = []

        obj_file_pattern = os.path.join(package.dir_path, obj_name)
        obj_file_pattern = f'{obj_file_pattern}.{obj_code}.*'

        mod_log().debug('Searching for object files: %s', obj_file_pattern)
        for source_file in glob.glob(obj_file_pattern):
            if source_file.endswith('.xml'):
                continue

            mod_log().debug('Adding file: %s', source_file)
            other_files.append(source_file)

        obj = RepoObject(obj_code, obj_name, os.path.join(package.dir_path, obj_file_name), package, other_files)
        self._objects.append(obj)
        self.mark_file_used(obj.path)

        return obj

    def add_package_dir(self, dir_path, parent=None):
        """add new directory package"""

        if parent:
            dir_path = os.path.join(parent.dir_path, dir_path)

        if not dir_path.startswith('./'):
            raise sap.errors.SAPCliError(f'Package dirs must start with "./": {dir_path}')

        pkg_file = os.path.join(dir_path, 'package.devc.xml', )
        if not os.path.isfile(pkg_file):
            raise sap.errors.SAPCliError(f'Not a package directory: {dir_path}')

        mod_log().debug('Adding new package dir: %s', dir_path)

        # Skip the first path part to ignore .
        parts = dir_path.split('/')[1:]
        if len(parts) < len(self._dir_prefix):
            raise sap.errors.SAPCliError(f'Sub-package dir {dir_path} not in starting folder'
                                         f' {self._config.STARTING_FOLDER}')

        for prefix in self._dir_prefix:
            if parts[0] != prefix:
                raise sap.errors.SAPCliError(f'Sub-package dir {dir_path} not in starting folder'
                                             f' {self._config.STARTING_FOLDER}')

            del parts[0]

        if parts and parts[0]:
            pkg_name = self._pkg_name_bldr(parts)
        else:
            pkg_name = self._name

        pkg = RepoPackage(pkg_name, pkg_file, dir_path, parent)
        self._packages[dir_path] = pkg
        self.mark_file_used(pkg_file)

        return pkg


def _is_supported(obj_type):
    return OBJECT_HANDLERS.for_metadata_file(obj_type, 'xml') is not None or obj_type in OBJECT_CHECKIN_HANDLERS


def _load_objects(repo):
    # packages
    # ddic
    # interfaces
    # classes
    # programs + includes

    abap_dir = f'.{repo.config.STARTING_FOLDER}'

    mod_log().debug('Loading ABAP dir: %s', abap_dir)

    repo.add_package_dir(abap_dir)

    for root, dirs, files in os.walk(abap_dir):
        mod_log().debug('Analyzing package dir: %s', root)

        package = repo.find_package_by_path(root)

        for obj_file_name in files:
            repo.add_file(os.path.join(root, obj_file_name))

            obj_name_parts = obj_file_name.split('.')
            if len(obj_name_parts) < 2:
                continue

            obj_type, suffix = obj_name_parts[-2:]
            if suffix != 'xml' or not _is_supported(obj_type):
                continue

            repo.add_object(obj_file_name, package)

        for sub_dir in dirs:
            repo.add_package_dir(sub_dir, parent=package)


def _get_config(starting_folder, console):
    conf_file_path = '.abapgit.xml'

    try:
        with open(conf_file_path, 'r', encoding='utf-8') as conf_file:
            conf_file_contents = conf_file.read()
            config = sap.platform.abap.abapgit.DOT_ABAP_GIT.from_xml(conf_file_contents)

            if config.STARTING_FOLDER != starting_folder:
                console.printout(f'Using starting-folder from .abapgit.xml: {config.STARTING_FOLDER}')
    except OSError as ex:
        if ex.errno != errno.ENOENT:
            raise

        if starting_folder is None:
            config = sap.platform.abap.abapgit.DOT_ABAP_GIT.for_new_repo()
        else:
            config = sap.platform.abap.abapgit.DOT_ABAP_GIT.for_new_repo(STARTING_FOLDER=starting_folder)

    return config


def prepare_package(repo_package):
    """Reads the file of the package without accessing the system"""

    devc = DEVC()
    with open(repo_package.path, encoding='utf-8') as devc_file:
        sap.platform.abap.from_xml(devc, devc_file.read())

    return devc


def checkin_package(connection, repo_package, args, prepared=None):
    """Checkin repository package"""

    devc = prepared or prepare_package(repo_package)

    sap.cli.core.printout(f'Creating Package: {repo_package.name} {devc.CTEXT}')

    metadata = sap.adt.ADTCoreData(language='EN', master_language='EN', responsible=connection.user.upper(),
                                   description=devc.CTEXT)

    package = sap.adt.Package(connection, repo_package.name.upper(), metadata=metadata)
    package.set_package_type('development')

    if repo_package.parent is not None:
        package.super_package.name = repo_package.parent.name.upper()

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

    domains = []
    dataelements = []
    structures = []
    ddic = []
    behaviors = []
    libs = []
    bins = []
    others = []

    for obj in objects:
        # Domains go first because other DDIC objects are typed by them
        if obj.code in ['doma']:
            domains.append(obj)
        # Data elements are typed by domains and structures are typed by them
        elif obj.code in ['dtel']:
            dataelements.append(obj)
        # Structures go before table types because table types use them as row types
        elif obj.code in ['tabl']:
            structures.append(obj)
        # abapGit deserializes data definitions in the DDIC step too
        elif obj.code in ['ttyp', 'ddls']:
            ddic.append(obj)
        # Behavior definitions refer to their behavior pools and behavior
        # pools are classes FOR BEHAVIOR OF behavior definitions, hence they
        # must be activated together but the behavior definitions go first
        elif obj.code in ['bdef']:
            behaviors.append(obj)
        elif obj.code in ['intf', 'clas']:
            libs.append(obj)
        elif obj.code in ['prog']:
            bins.append(obj)
        else:
            others.append(obj)

    return [domains + dataelements + structures + ddic, behaviors + libs, bins, others]


OBJECT_CHECKIN_HANDLERS: dict = {}


# Functions reading and checking the files of objects without accessing
# the system
OBJECT_CHECKIN_PREPARERS: dict = {}


def _get_preparer(obj_type):
    handler = OBJECT_HANDLERS.for_metadata_file(obj_type, 'xml')
    if handler is not None:
        return handler.prepare

    return OBJECT_CHECKIN_PREPARERS[obj_type]


def _prepare_repository(repo, console):
    """Reads and checks the files of all packages and objects before
       accessing the system to avoid long running checkins failing at the end
       because of a file which could not be checked in. Reports all problems
       and returns the prepared data by file paths.
    """

    prepared = {}
    problems = 0

    preparations = [(package.path, prepare_package, package) for package in repo.packages]
    preparations += [(obj.path, _get_preparer(obj.code), obj) for obj in repo.objects]

    for path, prepare, repo_item in preparations:
        try:
            prepared[path] = prepare(repo_item)
        # InputError (e.g. invalid XML) is not derived from SAPCliError
        except sap.errors.FatalError as ex:
            console.printerr(f'{path}: {ex}')
            problems += 1

    if problems:
        raise sap.errors.SAPCliError(f'Cannot check in {problems} files - nothing has been changed')

    return prepared


def _checkin_dependency_group(connection, repo, group, console, corrnr, check_before_save=False, prepared=None):
    inactive_objects = sap.adt.objects.ADTObjectReferences()

    for repo_obj in group:
        prepared_obj = (prepared or {}).get(repo_obj.path)

        # A failure stops the checkin because the objects using the object
        # would fail later anyway
        handler = OBJECT_HANDLERS.for_metadata_file(repo_obj.code, 'xml')
        if handler is not None:
            result = handler.checkin(CheckinContext(connection, repo_obj.package.name, corrnr, check_before_save),
                                     repo_obj, prepared_obj)
        else:
            obj_handler = OBJECT_CHECKIN_HANDLERS.get(repo_obj.code)

            if obj_handler is None:
                console.printerr(f'Object not supported: {repo_obj.path}')
                continue

            result = obj_handler(connection, repo_obj, corrnr, check_before_save=check_before_save,
                                 prepared=prepared_obj)

        for abap_obj in result.abap_objects:
            inactive_objects.add_object(abap_obj)

        for used_file in result.used_files:
            repo.mark_file_used(used_file)

    return inactive_objects


def _activate(connection, inactive_objects, console):
    sap.cli.wb.activate(connection, inactive_objects, console)


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
# pylint: disable=too-many-locals
def do_checkin_directory(connection, args):
    """Synchronize directory structure with ABAP package structure"""

    console = args.console_factory()

    top_dir = '.'
    if args.starting_folder:
        top_dir = os.path.join(top_dir, args.starting_folder)

    if not os.path.isdir(top_dir):
        console.printerr(f'Cannot check-in ABAP objects from "{top_dir}": not a directory')
        return 1

    config = _get_config(args.starting_folder, console)
    repo = Repository(args.name, config)

    flag = getattr(args, 'check', None)
    check_before_save = flag if flag is not None else config_get('check_before_save', False)

    try:
        _load_objects(repo)

        console.printout('Checking files ...')
        prepared = _prepare_repository(repo, console)

        console.printout('Creating packages ...')
        for package in repo.packages:
            checkin_package(connection, package, args, prepared=prepared.get(package.path))

        groups = _resolve_dependencies(repo.objects)

        for activation_group in groups:
            console.printout('Creating objects ...')
            inactive_objects = _checkin_dependency_group(
                connection, repo, activation_group, console, args.corrnr,
                check_before_save=check_before_save, prepared=prepared,
            )

            if inactive_objects.references:
                console.printout('Activating objects ...')
                _activate(connection, inactive_objects, console)

        for unused_file in repo.unused_files:
            console.printerr(f'Unused file: {unused_file}')
    except sap.adt.checks.ObjectCheckFindings as findings:
        for line in str(findings).splitlines():
            console.printerr(line)
        return 1
    except sap.errors.SAPCliError as ex:
        console.printerr(f'Checkin failed: {ex}')
        return 1

    return 0
