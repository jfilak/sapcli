# pylint: disable=too-many-lines
"""ADT Object import"""
import os
import re
import glob
import errno
import typing

from sap import get_logger

import sap.errors
import sap.cli.core
import sap.platform.abap.abapgit
from sap.platform.abap.ddic import (
    VSEOCLASS,
    DESCRIPTIONS_SUB,
    PROGDIR,
    CUA,
    TPOOL,
    VSEOINTERF,
    DEVC,
    SUBC_EXECUTABLE_PROGRAM,
    SUBC_INCLUDE,
    AREAT,
    INCLUDES,
    FUNCTIONS,
    DD40V,
    DD42V_TABLE,
    DD43V_TABLE,
    DD40L_EXTRA,
    DD40V_ACCESSMODE_TO_ADT,
    DD40V_KEYDEF_TO_ADT,
    DD40V_KEYKIND_TO_ADT,
    DDLS,
    DCLS,
    DDLX,
    BDEF,
    DD02V,
    DD03P_TABLE,
    DD01V,
    DD07V_TAB,
    DD01L_EXTRA,
    TABCLASS_STRUCTURE,
    DD02V_EXCLASS_TO_DDL,
    DDIC_DATATYPE_TO_DDL,
)
import sap.adt
import sap.adt.checks
import sap.adt.objects
import sap.adt.errors
import sap.adt.textelements
import sap.adt.wb
import sap.cli.wb
from sap.config import config_get


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


class ObjectCheckinResult(typing.NamedTuple):
    """Result of a single ADT object checkin handler"""

    abap_objects: list
    used_files: list


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
            if suffix != 'xml' or obj_type not in OBJECT_CHECKIN_HANDLERS:
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


def checkin_package(connection, repo_package, args):
    """Checkin repository package"""

    devc = DEVC()
    with open(repo_package.path, encoding='utf-8') as devc_file:
        sap.platform.abap.from_xml(devc, devc_file.read())

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

    return [domains + structures + ddic, behaviors + libs, bins, others]


def checkin_intf(connection, repo_obj, corrnr=None, check_before_save=False):
    """Checkin ADT Interface"""

    sap.cli.core.printout('Creating Interface:', repo_obj.name)

    if not repo_obj.files:
        raise sap.adt.errors.ExceptionCheckinFailure(f'No source file for interface {repo_obj.name}')

    if len(repo_obj.files) > 1:
        raise sap.adt.errors.ExceptionCheckinFailure(f'Too many source files for interface {repo_obj.name}: %s'
                                                     % (','.join(repo_obj.files)))

    source_file = repo_obj.files[0]

    if not source_file.endswith('.abap'):
        raise sap.adt.errors.ExceptionCheckinFailure(f'No .abap suffix of source file for interface {repo_obj.name}')

    with open(repo_obj.path, encoding='utf-8') as abap_data_file:
        # DESCRIPTIONS_SUB is parsed only to detect abapGit XML format changes
        # - ADT generates the sub-component descriptions from source code
        abap_data = sap.platform.abap.abapgit.from_xml(
            [VSEOINTERF, sap.platform.abap.abapgit.OptionalBody(DESCRIPTIONS_SUB)],
            abap_data_file.read())['VSEOINTERF']

    metadata = sap.adt.ADTCoreData(language='EN', master_language='EN', responsible=connection.user.upper(),
                                   description=abap_data.DESCRIPT)
    interface = sap.adt.Interface(connection, repo_obj.name.upper(), package=repo_obj.package.name, metadata=metadata)

    try:
        interface.create(corrnr)
    except sap.adt.errors.ExceptionResourceAlreadyExists as err:
        mod_log().info(err.message)

    sap.cli.core.printout('Writing Interface:', repo_obj.name)
    with open(source_file, 'r', encoding='utf-8') as source:
        _write_source_file(source.read(), interface, corrnr=corrnr,
                           source_label=source_file,
                           check_before_save=check_before_save)

    return ObjectCheckinResult([interface], [source_file])


def _text_symbols_from_tpool(tpool, object_name, known_ids=(), supported_ids=('I',)):
    """Returns text symbols (TPOOL entries with ID I) and reports the other
       entries not handled by the caller (known_ids) as skipped.
    """

    text_symbols = []

    for text in tpool:
        if text.ID in supported_ids:
            text_symbols.append(sap.adt.textelements.TextSymbol(text.KEY, text.ENTRY, int(text.LENGTH)))
        elif text.ID not in known_ids:
            entry = f'{text.ID} {text.KEY}' if text.KEY else text.ID
            sap.cli.core.printerr(f'Skipping unsupported text pool entry {entry} of {object_name}')

    return text_symbols


def _write_text_symbols(text_elements, text_symbols, corrnr):
    """Replaces text symbols of the given text elements"""

    with text_elements.open_editor(corrnr=corrnr) as editor:
        editor.write(sap.adt.textelements.serialize_symbols(text_symbols))


def checkin_clas(connection, repo_obj, corrnr=None, check_before_save=False):
    """Checkin ADT Clas"""
    # pylint: disable=too-many-locals

    sap.cli.core.printout('Creating Class:', repo_obj.name)

    if not repo_obj.files:
        raise sap.adt.errors.ExceptionCheckinFailure(f'No source file for class {repo_obj.name}')

    with open(repo_obj.path, encoding='utf-8') as abap_data_file:
        # DESCRIPTIONS_SUB is parsed only to detect abapGit XML format changes
        # - ADT generates the sub-component descriptions from source code
        results = sap.platform.abap.abapgit.from_xml(
            [VSEOCLASS, sap.platform.abap.abapgit.OptionalBody(TPOOL),
             sap.platform.abap.abapgit.OptionalBody(DESCRIPTIONS_SUB)],
            abap_data_file.read())

    abap_data = results['VSEOCLASS']
    text_symbols = _text_symbols_from_tpool(results.get('TPOOL', []), repo_obj.name)

    metadata = sap.adt.ADTCoreData(language='EN', master_language='EN', responsible=connection.user.upper(),
                                   description=abap_data.DESCRIPT)
    clas = sap.adt.Class(connection, repo_obj.name.upper(), package=repo_obj.package.name, metadata=metadata)

    try:
        clas.create(corrnr)
    except sap.adt.errors.ExceptionResourceAlreadyExists as exc:
        mod_log().info('Class already exists. Recreating.')
        clas.fetch()

        # pylint: disable=no-member
        if clas.reference.name != repo_obj.package.name:
            raise sap.adt.errors.ExceptionCheckinFailure(f'Cannot checkin class {repo_obj.name} into package'
                                                         f' {repo_obj.package.name}. It already exists in package'
                                                         f' {clas.reference.name}.') from exc

        clas.delete(corrnr)
        # Recreate class object to avoid stale data, which causes create to fail
        clas = sap.adt.Class(connection, repo_obj.name.upper(), package=repo_obj.package.name, metadata=metadata)
        clas.create(corrnr)

    used_files = []

    for source_file in repo_obj.files:
        if not source_file.endswith('.abap'):
            raise sap.adt.errors.ExceptionCheckinFailure(f'No .abap suffix of source file for class {repo_obj.name}:'
                                                         f' {source_file}')

        class_parts = {
            'clas': clas,
            'locals_def': clas.definitions,
            'locals_imp': clas.implementations,
            'testclasses': clas.test_classes,
        }

        sub_obj_id = source_file.split('.')[-2]
        sub_obj = class_parts.get(sub_obj_id, None)
        if sub_obj is None:
            sap.cli.core.printerr(f'Unknown class part {source_file}')
            continue

        sap.cli.core.printout('Writing Clas:', repo_obj.name, sub_obj_id)

        with open(source_file, 'r', encoding='utf-8') as source:
            _write_source_file(source.read(), sub_obj, corrnr=corrnr,
                               source_label=source_file,
                               check_before_save=check_before_save)

        used_files.append(source_file)

    abap_objects = [clas]

    if text_symbols:
        sap.cli.core.printout('Writing Clas:', repo_obj.name, 'text elements')
        text_elements = sap.adt.textelements.ClassTextElements(connection, repo_obj.name.upper())
        _write_text_symbols(text_elements, text_symbols, corrnr)
        abap_objects.append(text_elements)

    return ObjectCheckinResult(abap_objects, used_files)


def checkin_prog(connection, repo_obj, corrnr=None, check_before_save=False):
    """Checkin ADT Program"""
    # pylint: disable=too-many-locals

    sap.cli.core.printout('Creating Program:', repo_obj.name)

    if not repo_obj.files:
        raise sap.adt.errors.ExceptionCheckinFailure(f'No source file for program {repo_obj.name}')

    if len(repo_obj.files) > 1:
        raise sap.adt.errors.ExceptionCheckinFailure(f'Too many source files for program {repo_obj.name}:'
                                                     f' %s' % (','.join(repo_obj.files)))

    source_file = repo_obj.files[0]

    if not source_file.endswith('.abap'):
        raise sap.adt.errors.ExceptionCheckinFailure(f'No .abap suffix of source file for program {repo_obj.name}')

    with open(repo_obj.path, encoding='utf-8') as abap_data_file:
        results = sap.platform.abap.abapgit.from_xml([PROGDIR, sap.platform.abap.abapgit.OptionalBody(CUA), TPOOL], abap_data_file.read())

    progdir = results['PROGDIR']
    # TODO: how to handle CUA?
    tpool = results['TPOOL']

    metadata = sap.adt.ADTCoreData(language='EN', master_language='EN', responsible=connection.user.upper())
    if progdir.SUBC == SUBC_EXECUTABLE_PROGRAM:
        program = sap.adt.Program(connection, repo_obj.name, package=repo_obj.package.name, metadata=metadata)
    elif progdir.SUBC == SUBC_INCLUDE:
        sap.cli.core.printout('Creating Include:', repo_obj.name)
        program = sap.adt.Include(connection, repo_obj.name, package=repo_obj.package.name, metadata=metadata)
    else:
        raise sap.adt.errors.ExceptionCheckinFailure(f'Unknown program type {progdir.SUBC}')

    for text in tpool:
        if text.ID == 'R':
            program.description = text.ENTRY

    # ADT does not allow editing text elements of includes
    supported_ids = ('I',) if progdir.SUBC == SUBC_EXECUTABLE_PROGRAM else ()
    text_symbols = _text_symbols_from_tpool(tpool, repo_obj.name, known_ids=('R',), supported_ids=supported_ids)

    try:
        program.create(corrnr)
    except sap.adt.errors.ExceptionResourceCreationFailure as err:
        if not str(err).endswith(f'A program or include already exists with the name {repo_obj.name.upper()}'):
            raise

        mod_log().info(err.message)

    sap.cli.core.printout('Writing Program:', repo_obj.name)
    with open(source_file, 'r', encoding='utf-8') as source:
        _write_source_file(source.read(), program, corrnr=corrnr,
                           source_label=source_file,
                           check_before_save=check_before_save)

    abap_objects = [program]

    if text_symbols:
        sap.cli.core.printout('Writing Program:', repo_obj.name, 'text elements')
        text_elements = sap.adt.textelements.ProgramTextElements(connection, repo_obj.name.upper())
        _write_text_symbols(text_elements, text_symbols, corrnr)
        # ADT does not activate inactive text elements together with the program
        abap_objects.append(text_elements)

    return ObjectCheckinResult(abap_objects, [source_file])


def _check_fugr_source_files(repo_obj, functions, includes):
    """Check that all functions and includes have source files"""

    for func in functions:
        function_name = func.FUNCNAME.lower()
        function_file_path = repo_obj.path[:-4] + f'.{function_name}' + '.abap'
        if function_file_path not in repo_obj.files:
            raise sap.adt.errors.ExceptionCheckinFailure(f'No source file for function {function_name}')

    for include in includes:
        include_name = include.lower()
        include_file_path = repo_obj.path[:-4] + f'.{include_name}' + '.abap'
        if include_file_path not in repo_obj.files:
            raise sap.adt.errors.ExceptionCheckinFailure(f'No source file for include {include_name}')


def _write_source_file(source_code, adt_object, corrnr=None, source_label=None,
                       check_before_save=False):
    """Write ``source_code`` to ``adt_object``.

    When ``check_before_save`` is ``True`` (because the user passed
    ``--check`` or set ``SAPCLI_CHECK_BEFORE_SAVE=true``), abapCheckRun
    runs first and a findings exception is raised if it reports errors.

    Independently of the flag, if the PUT to ``source/main`` raises
    :exc:`sap.adt.errors.ExceptionResourceSaveFailure`, abapCheckRun is
    run once on the source we tried to write so the user gets a
    readable diagnostic instead of the cryptic save error. If the
    check has nothing to say, the original failure carries the real
    reason (lock, missing inactive version, ...) and is re-raised.
    """

    if check_before_save:
        result = sap.adt.checks.run_object_check(adt_object, source_code)
        if result.has_errors:
            raise sap.adt.checks.ObjectCheckFindings(
                adt_object, result, source_label=source_label
            )

    try:
        with adt_object.open_editor(corrnr=corrnr) as editor:
            editor.write(source_code)
    except sap.adt.errors.ExceptionResourceSaveFailure as save_exc:
        result = sap.adt.checks.run_object_check(adt_object, source_code)
        if result.has_errors:
            raise sap.adt.checks.ObjectCheckFindings(
                adt_object, result, source_label=source_label
            ) from save_exc
        raise


def _write_adt_object_source_file(path_prefix, adt_object, corrnr=None,
                                  check_before_save=False):
    """Write source file for ADT object"""

    adt_object_file_path = path_prefix + f'.{adt_object.name.lower()}' + '.abap'
    with open(adt_object_file_path, 'r', encoding='utf-8') as source:
        _write_source_file(source.read(), adt_object, corrnr,
                           source_label=adt_object_file_path,
                           check_before_save=check_before_save)

    return adt_object_file_path


def _format_function(source_code):
    """Format parameters of function

    Original source code:
    ```
        FUNCTION ztest_function.
        *"----------------------------------------------------------------------
        *"*"Local Interface:
        *"  IMPORTING
        *"     VALUE(IV_PARAM1) TYPE  STRING
        *"  EXPORTING
        *"     VALUE(EV_PARAM2) TYPE  STRING
        *"----------------------------------------------------------------------
        ...
        ENDFUNCTION.
    ```
    Formatted source code:
    ```
        FUNCTION ztest_function
        IMPORTING
        VALUE(IV_PARAM1) TYPE STRING
        EXPORTING
        VALUE(EV_PARAM2) TYPE STRING
        .
        ...
        ENDFUNCTION.
    ```
    """

    source_lines = source_code.split('\n')
    start_block, end_block = sap.adt.function.FunctionModule.get_parameters_block(source_lines)
    if end_block == 0:
        # Source code is in ADT format
        return '\n'.join(source_lines)

    source_lines[0] = source_lines[0].replace('.', '')  # Remove dot at the end of first line
    parameters = sap.adt.function.FunctionModule.parse_function_parameters(source_lines[start_block:end_block])
    adt_parameters_block = []
    for param_type, params in parameters.items():
        if not params:
            continue

        adt_parameters_block.append(f'{param_type}')
        adt_parameters_block += params

    adt_parameters_block.append('.')  # Add dot at the end of the parameters block
    source_lines[start_block:end_block + 1] = adt_parameters_block
    return '\n'.join(source_lines)


def _write_function_source_code(path_prefix, adt_object, corrnr=None,
                                check_before_save=False):
    """Write source code for function. If function is in ababGit format, change it to ADT format"""

    source_file_path = path_prefix + f'.{adt_object.name.lower()}' + '.abap'
    with open(source_file_path, 'r', encoding='utf-8') as source:
        source_code = source.read()

    source_code = _format_function(source_code)
    _write_source_file(source_code, adt_object, corrnr,
                       source_label=source_file_path,
                       check_before_save=check_before_save)

    return source_file_path


def create_function_module(connection, func, function_group, metadata, corrnr):
    """Create Function Module"""

    function_module = sap.adt.FunctionModule(connection, func.FUNCNAME, function_group.name, metadata=metadata)
    function_module.description = func.SHORT_TEXT

    sap.cli.core.printout('Creating Function Module:', function_module.name)
    try:
        function_module.create(corrnr)
    except sap.adt.errors.ExceptionResourceAlreadyExists as err:
        mod_log().info(err.message)

    if func.REMOTE_CALL == 'R':
        function_module.processing_type = 'rfc'
        lock_handle = function_module.lock()
        with function_module.open_editor(lock_handle, corrnr) as fn_editor:
            fn_editor.push()

    return function_module


# pylint: disable=too-many-locals
def checkin_fugr(connection, repo_obj, corrnr=None, check_before_save=False):
    """Checkin ADT Function Group"""

    sap.cli.core.printout('Creating Function Group:', repo_obj.name)
    with open(repo_obj.path, encoding='utf-8') as abap_data_file:
        results = sap.platform.abap.abapgit.from_xml([AREAT, INCLUDES, FUNCTIONS], abap_data_file.read())

    includes = results['INCLUDES']
    functions = results['FUNCTIONS']

    _check_fugr_source_files(repo_obj, functions, includes)

    metadata = sap.adt.ADTCoreData(language='EN', master_language='EN', responsible=connection.user.upper())
    function_group = sap.adt.FunctionGroup(connection, repo_obj.name.upper(), package=repo_obj.package.name,
                                           metadata=metadata)
    function_group.description = results['AREAT']

    try:
        function_group.create(corrnr)
    except sap.adt.errors.ExceptionResourceAlreadyExists as err:
        mod_log().info(err.message)

    abap_objs_inactive = [function_group]
    used_files = []

    for include in includes:
        include_obj = sap.adt.FunctionInclude(connection, include, function_group.name, metadata=metadata)
        abap_objs_inactive.append(include_obj)

        sap.cli.core.printout('Creating Function Group Include:', include_obj.name)
        try:
            include_obj.create(corrnr)
        except sap.adt.errors.ExceptionResourceCreationFailure as err:
            if not str(err).endswith('already exists'):
                raise

            mod_log().info(err.message)

        sap.cli.core.printout('Writing Function Group Include:', include_obj.name)
        used_files.append(_write_adt_object_source_file(repo_obj.path[:-4], include_obj, corrnr=corrnr,
                                                        check_before_save=check_before_save))

    for func in functions:
        function_module = create_function_module(connection, func, function_group, metadata, corrnr)
        abap_objs_inactive.append(function_module)

        sap.cli.core.printout('Writing Function Module:', function_module.name)
        used_files.append(_write_function_source_code(repo_obj.path[:-4], function_module, corrnr=corrnr,
                                                      check_before_save=check_before_save))

    return ObjectCheckinResult(abap_objs_inactive, used_files)


def _dd40v_code_to_adt(mapping, dd40v, field, object_name):
    """Returns ADT value of the given DD40V field"""

    code = getattr(dd40v, field)
    try:
        return mapping[code]
    except KeyError as ex:
        raise sap.adt.errors.ExceptionCheckinFailure(
            f'Unsupported {field} "{code}" of table type {object_name}') from ex


# pylint: disable=unused-argument
def checkin_ttyp(connection, repo_obj, corrnr=None, check_before_save=False):
    """Checkin ADT Table Type"""

    sap.cli.core.printout('Creating Table Type:', repo_obj.name)

    with open(repo_obj.path, encoding='utf-8') as abap_data_file:
        # DD40L_EXTRA is parsed only to accept files of newer abapGit versions
        results = sap.platform.abap.abapgit.from_xml(
            [DD40V, sap.platform.abap.abapgit.OptionalBody(DD42V_TABLE),
             sap.platform.abap.abapgit.OptionalBody(DD43V_TABLE),
             sap.platform.abap.abapgit.OptionalBody(DD40L_EXTRA)],
            abap_data_file.read())

    dd40v = results['DD40V']
    if dd40v.ROWKIND not in (None, 'S', 'E', 'L') or dd40v.REFTYPE or dd40v.TTYPKIND:
        raise sap.adt.errors.ExceptionCheckinFailure(f'Unsupported row type of table type {repo_obj.name}:'
                                                     ' only dictionary and predefined types are supported')

    access_type = _dd40v_code_to_adt(DD40V_ACCESSMODE_TO_ADT, dd40v, 'ACCESSMODE', repo_obj.name)
    key_definition = _dd40v_code_to_adt(DD40V_KEYDEF_TO_ADT, dd40v, 'KEYDEF', repo_obj.name)
    key_kind = _dd40v_code_to_adt(DD40V_KEYKIND_TO_ADT, dd40v, 'KEYKIND', repo_obj.name)
    key_components = [line.KEYFIELD for line in results.get('DD42V', []) if not line.SECKEYNAME]

    if results.get('DD43V'):
        sap.cli.core.printerr(f'Skipping unsupported secondary keys of {repo_obj.name}')

    metadata = sap.adt.ADTCoreData(language='EN', master_language='EN', responsible=connection.user.upper(),
                                   description=dd40v.DDTEXT)
    tabletype = sap.adt.TableType(connection, repo_obj.name.upper(), package=repo_obj.package.name,
                                  metadata=metadata)

    try:
        tabletype.create(corrnr)
    except sap.adt.errors.ExceptionResourceAlreadyExists as err:
        mod_log().info(err.message)

    # ADT fills in the definition defaults on creation
    tabletype.fetch()

    if dd40v.ROWKIND:
        tabletype.set_dictionary_row_type(dd40v.ROWTYPE)
    else:
        tabletype.set_predefined_row_type(dd40v.DATATYPE, dd40v.LENG or '0', dd40v.DECIMALS or '0')

    tabletype.access_type = access_type
    tabletype.set_primary_key(key_definition, key_kind, key_components)

    sap.cli.core.printout('Writing Table Type:', repo_obj.name)
    with tabletype.open_editor(corrnr=corrnr) as editor:
        editor.push()

    return ObjectCheckinResult([tabletype], [])


# pylint: disable=too-many-arguments
def _checkin_cds_source(connection, repo_obj, abap_type, get_description, adt_type, source_suffix, label, corrnr,
                        check_before_save):
    """Creates the CDS source object described by the abapGit XML file of the
       given type and writes its source code. Returns the ADT object and the
       path of the source code file.
    """

    sap.cli.core.printout(f'Creating {label}:', repo_obj.name)

    source_file = repo_obj.path[:-4] + source_suffix
    if source_file not in repo_obj.files:
        raise sap.adt.errors.ExceptionCheckinFailure(f'No source file for {label.lower()} {repo_obj.name}')

    with open(repo_obj.path, encoding='utf-8') as abap_data_file:
        abap_data = sap.platform.abap.abapgit.from_xml([abap_type], abap_data_file.read())[abap_type.__name__]

    metadata = sap.adt.ADTCoreData(language='EN', master_language='EN', responsible=connection.user.upper(),
                                   description=get_description(abap_data))
    adt_object = adt_type(connection, repo_obj.name.upper(), package=repo_obj.package.name, metadata=metadata)

    try:
        adt_object.create(corrnr)
    except sap.adt.errors.ExceptionResourceAlreadyExists as err:
        mod_log().info(err.message)

    sap.cli.core.printout(f'Writing {label}:', repo_obj.name)
    with open(source_file, 'r', encoding='utf-8') as source:
        _write_source_file(source.read(), adt_object, corrnr=corrnr,
                           source_label=source_file,
                           check_before_save=check_before_save)

    return (adt_object, source_file)


def checkin_ddls(connection, repo_obj, corrnr=None, check_before_save=False):
    """Checkin ADT Data Definition"""

    ddl, source_file = _checkin_cds_source(connection, repo_obj, DDLS, lambda ddls: ddls.DDTEXT,
                                           sap.adt.DataDefinition, '.asddls', 'Data Definition', corrnr,
                                           check_before_save)

    used_files = [source_file]

    # The base info lists the objects the data definition uses and ADT
    # computes it from the source code
    baseinfo_file = repo_obj.path[:-4] + '.baseinfo'
    if baseinfo_file in repo_obj.files:
        used_files.append(baseinfo_file)

    return ObjectCheckinResult([ddl], used_files)


def checkin_dcls(connection, repo_obj, corrnr=None, check_before_save=False):
    """Checkin ADT Access Control"""

    dcl, source_file = _checkin_cds_source(connection, repo_obj, DCLS, lambda dcls: dcls.DDTEXT,
                                           sap.adt.AccessControl, '.asdcls', 'Access Control', corrnr,
                                           check_before_save)

    return ObjectCheckinResult([dcl], [source_file])


def checkin_ddlx(connection, repo_obj, corrnr=None, check_before_save=False):
    """Checkin ADT Metadata Extension"""

    # Old abapGit versions stored the source code in the XML file but abapGit
    # has been writing it to the file .asddlxs for years
    ddlx, source_file = _checkin_cds_source(connection, repo_obj, DDLX, lambda ddlx: ddlx.METADATA.DESCRIPTION,
                                            sap.adt.MetadataExtension, '.asddlxs', 'Metadata Extension', corrnr,
                                            check_before_save)

    return ObjectCheckinResult([ddlx], [source_file])


def checkin_bdef(connection, repo_obj, corrnr=None, check_before_save=False):
    """Checkin ADT Behavior Definition"""

    bdef, source_file = _checkin_cds_source(connection, repo_obj, BDEF, lambda bdef: bdef.DESCRIPTION,
                                            sap.adt.BehaviorDefinition, '.asbdef', 'Behavior Definition', corrnr,
                                            check_before_save)

    return ObjectCheckinResult([bdef], [source_file])


# .INCLUDE or .INCLU-<SUFFIX> but not .INCLU--AP of append structures
INCLUDE_FIELDNAME = re.compile(r'\.INCLU(DE|-(?P<suffix>\w+))')


def _ddl_name(name):
    """Returns the DDL name - delimited if it is not a plain identifier"""

    name = name.lower()
    if re.fullmatch(r'[a-z0-9_/]+', name):
        return name

    return f'"{name}"'


def _ddl_string(value):
    """Returns the DDL string literal"""

    escaped = value.replace("'", "''")
    return f"'{escaped}'"


def _structure_field_type(field, object_name):
    """Returns DDL type of the given structure field"""

    if field.ROLLNAME:
        if field.COMPTYPE == 'R':
            raise sap.adt.errors.ExceptionCheckinFailure(
                f'Unsupported reference type of the field {field.FIELDNAME} of structure {object_name}')

        return field.ROLLNAME.lower()

    try:
        ddl_type, params = DDIC_DATATYPE_TO_DDL[field.DATATYPE]
    except KeyError as ex:
        raise sap.adt.errors.ExceptionCheckinFailure(
            f'Unsupported data type "{field.DATATYPE}" of the field {field.FIELDNAME} of structure {object_name}') from ex

    if params == 0:
        return f'abap.{ddl_type}'

    length = int(field.LENG or '0')
    if params == 1:
        return f'abap.{ddl_type}({length})'

    return f'abap.{ddl_type}({length},{int(field.DECIMALS or "0")})'


def _structure_field_reference(field, dd02v, fields, object_name):
    """Returns DDL annotation of the currency or unit reference of the given
       structure field.
    """

    # abapGit does not write data types of fields typed by data elements,
    # so only the data types of the field and of the referenced field in the
    # same structure can tell the kind of the reference
    datatypes = {field.DATATYPE}
    if field.REFTABLE == dd02v.TABNAME:
        datatypes.update(ref.DATATYPE for ref in fields if ref.FIELDNAME == field.REFFIELD)

    reference = _ddl_string(f'{field.REFTABLE.lower()}.{field.REFFIELD.lower()}')

    if datatypes & {'CURR', 'CUKY'}:
        return f'@Semantics.amount.currencyCode : {reference}'

    if datatypes & {'QUAN', 'UNIT'}:
        return f'@Semantics.quantity.unitOfMeasure : {reference}'

    raise sap.adt.errors.ExceptionCheckinFailure(
        f'Cannot determine whether the field {field.FIELDNAME} of structure {object_name}'
        ' refers to a currency or to a unit')


def build_structure_source(dd02v, fields, object_name):
    """Returns DDL source code of the structure described by the abapGit
       sections DD02V and DD03P.
    """

    lines = [f'@EndUserText.label : {_ddl_string(dd02v.DDTEXT or "")}']

    if dd02v.EXCLASS:
        try:
            lines.append(f'@AbapCatalog.enhancement.category : {DD02V_EXCLASS_TO_DDL[dd02v.EXCLASS]}')
        except KeyError as ex:
            raise sap.adt.errors.ExceptionCheckinFailure(
                f'Unsupported enhancement category "{dd02v.EXCLASS}" of structure {object_name}') from ex

    lines.append(f'define structure {dd02v.TABNAME.lower()} {{')
    lines.append('')

    # Field names are aligned the same way as ADT and abapGit do
    width = max((len(_ddl_name(field.GROUPNAME or field.FIELDNAME)) for field in fields
                 if field.GROUPNAME or not field.FIELDNAME.startswith('.')), default=0)

    for field in fields:
        include = INCLUDE_FIELDNAME.fullmatch(field.FIELDNAME)
        if include:
            definition = f'include {field.PRECFIELD.lower()}'
            if include.group('suffix'):
                definition += f' with suffix {include.group("suffix").lower()}'

            if field.GROUPNAME:
                definition = f'{_ddl_name(field.GROUPNAME).ljust(width)} : {definition}'

            lines.append(f'  {definition};')
            continue

        if field.FIELDNAME.startswith('.'):
            raise sap.adt.errors.ExceptionCheckinFailure(
                f'Unsupported field {field.FIELDNAME} of structure {object_name}')

        # abapGit writes texts of fields typed by data elements but they
        # belong to the data elements
        if not field.ROLLNAME and field.DDTEXT:
            lines.append(f'  @EndUserText.label : {_ddl_string(field.DDTEXT)}')

        if field.REFFIELD:
            lines.append(f'  {_structure_field_reference(field, dd02v, fields, object_name)}')

        lines.append(f'  {_ddl_name(field.FIELDNAME).ljust(width)} : {_structure_field_type(field, object_name)};')

    lines.append('')
    lines.append('}')

    return '\n'.join(lines)


def checkin_tabl(connection, repo_obj, corrnr=None, check_before_save=False):
    """Checkin ADT Structure"""

    sap.cli.core.printout('Creating Structure:', repo_obj.name)

    with open(repo_obj.path, encoding='utf-8') as abap_data_file:
        try:
            results = sap.platform.abap.abapgit.from_xml(
                [DD02V, sap.platform.abap.abapgit.OptionalBody(DD03P_TABLE)],
                abap_data_file.read())
        except sap.errors.SAPCliError as ex:
            # e.g. foreign keys or search helps which are not supported yet
            raise sap.adt.errors.ExceptionCheckinFailure(
                f'Unsupported contents of structure {repo_obj.name}: {ex}') from ex

    dd02v = results['DD02V']
    if dd02v.TABCLASS != TABCLASS_STRUCTURE:
        raise sap.adt.errors.ExceptionCheckinFailure(
            f'Unsupported table category "{dd02v.TABCLASS}" of {repo_obj.name}: only structures are supported')

    source_code = build_structure_source(dd02v, results.get('DD03P_TABLE', []), repo_obj.name)

    metadata = sap.adt.ADTCoreData(language='EN', master_language='EN', responsible=connection.user.upper(),
                                   description=dd02v.DDTEXT)
    structure = sap.adt.Structure(connection, repo_obj.name.upper(), package=repo_obj.package.name,
                                  metadata=metadata)

    try:
        structure.create(corrnr)
    except sap.adt.errors.ExceptionResourceAlreadyExists as err:
        mod_log().info(err.message)

    sap.cli.core.printout('Writing Structure:', repo_obj.name)
    _write_source_file(source_code, structure, corrnr=corrnr, source_label=repo_obj.path,
                       check_before_save=check_before_save)

    return ObjectCheckinResult([structure], [])


def _abap_flag_to_adt(flag):
    """Returns ADT boolean value of the given ABAP flag"""

    return 'true' if flag else 'false'


# pylint: disable=unused-argument
def checkin_doma(connection, repo_obj, corrnr=None, check_before_save=False):
    """Checkin ADT Domain"""

    sap.cli.core.printout('Creating Domain:', repo_obj.name)

    with open(repo_obj.path, encoding='utf-8') as abap_data_file:
        try:
            # DD01L_EXTRA is parsed only to accept files of newer abapGit versions
            results = sap.platform.abap.abapgit.from_xml(
                [DD01V, sap.platform.abap.abapgit.OptionalBody(DD07V_TAB),
                 sap.platform.abap.abapgit.OptionalBody(DD01L_EXTRA)],
                abap_data_file.read())
        except sap.errors.SAPCliError as ex:
            # e.g. translations or long texts which are not supported yet
            raise sap.adt.errors.ExceptionCheckinFailure(
                f'Unsupported contents of domain {repo_obj.name}: {ex}') from ex

    dd01v = results['DD01V']

    metadata = sap.adt.ADTCoreData(language='EN', master_language='EN', responsible=connection.user.upper(),
                                   description=dd01v.DDTEXT)
    domain = sap.adt.Domain(connection, repo_obj.name.upper(), package=repo_obj.package.name, metadata=metadata)

    try:
        domain.create(corrnr)
    except sap.adt.errors.ExceptionResourceAlreadyExists as err:
        mod_log().info(err.message)

    # ADT accepts the content only in modifications of existing domains
    domain.fetch()
    domain.description = dd01v.DDTEXT

    type_information = domain.content.type_information
    type_information.datatype = dd01v.DATATYPE
    type_information.length = dd01v.LENG or '0'
    type_information.decimals = dd01v.DECIMALS or '0'

    output_information = domain.content.output_information
    output_information.length = dd01v.OUTPUTLEN or '0'
    output_information.style = dd01v.OUTPUTSTYLE or '00'
    output_information.conversion_exit = dd01v.CONVEXIT or ''
    output_information.sign_exists = _abap_flag_to_adt(dd01v.SIGNFLAG)
    output_information.lowercase = _abap_flag_to_adt(dd01v.LOWERCASE)
    output_information.ampm_format = _abap_flag_to_adt(dd01v.AMPMFORMAT)

    value_information = domain.content.value_information
    value_information.value_table_ref = sap.adt.domain.DomainValueTableRef()
    value_information.value_table_ref.name = dd01v.ENTITYTAB

    # abapGit renumbers the fixed values the same way
    value_information.fix_values = sap.adt.domain.DomainFixValues()
    for position, dd07v in enumerate(results.get('DD07V_TAB', []), start=1):
        fix_value = sap.adt.domain.DomainFixValue()
        fix_value.position = f'{position:04d}'
        fix_value.low = dd07v.DOMVALUE_L or ''
        fix_value.high = dd07v.DOMVALUE_H or ''
        fix_value.text = dd07v.DDTEXT or ''
        value_information.fix_values.append(fix_value)

    sap.cli.core.printout('Writing Domain:', repo_obj.name)
    with domain.open_editor(corrnr=corrnr) as editor:
        editor.push()

    return ObjectCheckinResult([domain], [])


OBJECT_CHECKIN_HANDLERS = {
    'intf': checkin_intf,
    'clas': checkin_clas,
    'prog': checkin_prog,
    'fugr': checkin_fugr,
    'ttyp': checkin_ttyp,
    'ddls': checkin_ddls,
    'dcls': checkin_dcls,
    'ddlx': checkin_ddlx,
    'bdef': checkin_bdef,
    'tabl': checkin_tabl,
    'doma': checkin_doma,
}


def _checkin_dependency_group(connection, repo, group, console, corrnr, check_before_save=False):
    inactive_objects = sap.adt.objects.ADTObjectReferences()

    for repo_obj in group:
        obj_handler = OBJECT_CHECKIN_HANDLERS.get(repo_obj.code)

        if obj_handler is None:
            console.printerr(f'Object not supported: {repo_obj.path}')
            continue

        try:
            result = obj_handler(connection, repo_obj, corrnr,
                                 check_before_save=check_before_save)
            for abap_obj in result.abap_objects:
                inactive_objects.add_object(abap_obj)

            for used_file in result.used_files:
                repo.mark_file_used(used_file)

        except sap.adt.errors.ExceptionCheckinFailure:
            console.printout(f'Object handled without activation: {repo_obj.path}')

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

        console.printout('Creating packages ...')
        for package in repo.packages:
            checkin_package(connection, package, args)

        groups = _resolve_dependencies(repo.objects)

        for activation_group in groups:
            console.printout('Creating objects ...')
            inactive_objects = _checkin_dependency_group(
                connection, repo, activation_group, console, args.corrnr,
                check_before_save=check_before_save,
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
