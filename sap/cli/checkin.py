# pylint: disable=too-many-lines
"""ADT Object import"""
import os
import re
import glob
import errno
import typing
from types import SimpleNamespace

from sap import get_logger

import sap.errors
import sap.cli.core
import sap.platform.abap.abapgit
from sap.platform.abap.ddic import (
    DEVC,
    BDEF,
    DD02V,
    DD03P_TABLE,
    DD01V,
    DD07V_TAB,
    DD01L_EXTRA,
    DD04V,
    DD04L_EXTRA,
    REFKIND_DOMAIN,
    TABCLASS_STRUCTURE,
    TABCLASS_TRANSPARENT,
    DD02V_EXCLASS_TO_DDL,
    DD02V_MAINFLAG_TO_DDL,
    DD09L,
    DDIC_DATATYPE_TO_DDL,
    DDIC_DATATYPE_TO_ADT,
)
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
from sap.fileformat.abapgit.cds import prepare_cds_source, checkin_cds_source
from sap.fileformat import HandlerRegistry, CheckinContext, ObjectCheckinResult

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


def prepare_bdef(repo_obj):
    """Reads and checks the files of the behavior definition"""

    return prepare_cds_source(repo_obj, BDEF, lambda bdef: bdef.DESCRIPTION, '.asbdef', 'Behavior Definition')


def checkin_bdef(connection, repo_obj, corrnr=None, check_before_save=False, prepared=None):
    """Checkin ADT Behavior Definition"""

    bdef, source_file = checkin_cds_source(
        CheckinContext(connection, repo_obj.package.name, corrnr, check_before_save), repo_obj,
        prepared or prepare_bdef(repo_obj), sap.adt.BehaviorDefinition, 'Behavior Definition')

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


def _structure_field_type(field, object_name, kind):
    """Returns DDL type of the given structure or table field"""

    if field.ROLLNAME:
        if field.COMPTYPE == 'R':
            raise sap.adt.errors.ExceptionCheckinFailure(
                f'Unsupported reference type of the field {field.FIELDNAME} of {kind} {object_name}')

        return field.ROLLNAME.lower()

    try:
        ddl_type, params = DDIC_DATATYPE_TO_DDL[field.DATATYPE]
    except KeyError as ex:
        raise sap.adt.errors.ExceptionCheckinFailure(
            f'Unsupported data type "{field.DATATYPE}" of the field {field.FIELDNAME} of {kind} {object_name}') from ex

    if params == 0:
        return f'abap.{ddl_type}'

    length = int(field.LENG or '0')
    if params == 1:
        return f'abap.{ddl_type}({length})'

    return f'abap.{ddl_type}({length},{int(field.DECIMALS or "0")})'


def _structure_field_reference(field, dd02v, fields, object_name, kind):
    """Returns DDL annotation of the currency or unit reference of the given
       structure or table field.
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
        f'Cannot determine whether the field {field.FIELDNAME} of {kind} {object_name}'
        ' refers to a currency or to a unit')


def _ddl_field_name(field):
    """Returns the DDL name of the given field including the keyword key"""

    name = _ddl_name(field.GROUPNAME or field.FIELDNAME)
    if field.KEYFLAG:
        return f'key {name}'

    return name


def _build_ddl_source(dd02v, fields, object_name, kind, annotations):
    """Returns DDL source code of the structure or table described by the
       abapGit sections DD02V and DD03P.
    """

    lines = [f'@EndUserText.label : {_ddl_string(dd02v.DDTEXT or "")}']

    if dd02v.EXCLASS:
        try:
            lines.append(f'@AbapCatalog.enhancement.category : {DD02V_EXCLASS_TO_DDL[dd02v.EXCLASS]}')
        except KeyError as ex:
            raise sap.adt.errors.ExceptionCheckinFailure(
                f'Unsupported enhancement category "{dd02v.EXCLASS}" of {kind} {object_name}') from ex

    lines.extend(annotations)
    lines.append(f'define {kind} {dd02v.TABNAME.lower()} {{')
    lines.append('')

    # Field names are aligned the same way as ADT and abapGit do
    width = max((len(_ddl_field_name(field)) for field in fields
                 if field.GROUPNAME or not field.FIELDNAME.startswith('.')), default=0)

    for field in fields:
        include = INCLUDE_FIELDNAME.fullmatch(field.FIELDNAME)
        if include:
            if field.KEYFLAG:
                raise sap.adt.errors.ExceptionCheckinFailure(
                    f'Unsupported key include {field.PRECFIELD} of {kind} {object_name}')

            definition = f'include {field.PRECFIELD.lower()}'
            if include.group('suffix'):
                definition += f' with suffix {include.group("suffix").lower()}'

            if field.GROUPNAME:
                definition = f'{_ddl_name(field.GROUPNAME).ljust(width)} : {definition}'

            lines.append(f'  {definition};')
            continue

        if field.FIELDNAME.startswith('.'):
            raise sap.adt.errors.ExceptionCheckinFailure(
                f'Unsupported field {field.FIELDNAME} of {kind} {object_name}')

        # abapGit writes texts of fields typed by data elements but they
        # belong to the data elements
        if not field.ROLLNAME and field.DDTEXT:
            lines.append(f'  @EndUserText.label : {_ddl_string(field.DDTEXT)}')

        if field.REFFIELD:
            lines.append(f'  {_structure_field_reference(field, dd02v, fields, object_name, kind)}')

        definition = f'{_ddl_field_name(field).ljust(width)} : {_structure_field_type(field, object_name, kind)}'
        if field.NOTNULL:
            definition += ' not null'

        lines.append(f'  {definition};')

    lines.append('')
    lines.append('}')

    return '\n'.join(lines)


def build_structure_source(dd02v, fields, object_name):
    """Returns DDL source code of the structure described by the abapGit
       sections DD02V and DD03P.
    """

    return _build_ddl_source(dd02v, fields, object_name, 'structure', [])


def build_table_source(dd02v, fields, object_name):
    """Returns DDL source code of the transparent table described by
       the abapGit sections DD02V and DD03P.
    """

    annotations = ['@AbapCatalog.tableCategory : #TRANSPARENT']

    if dd02v.CONTFLAG:
        annotations.append(f'@AbapCatalog.deliveryClass : #{dd02v.CONTFLAG}')

    try:
        annotations.append(f'@AbapCatalog.dataMaintenance : {DD02V_MAINFLAG_TO_DDL[dd02v.MAINFLAG or ""]}')
    except KeyError as ex:
        raise sap.adt.errors.ExceptionCheckinFailure(
            f'Unsupported data maintenance "{dd02v.MAINFLAG}" of table {object_name}') from ex

    return _build_ddl_source(dd02v, fields, object_name, 'table', annotations)


def _write_table_settings(connection, name, dd09l, corrnr):
    """Writes the technical settings of the table - ADT creates them
       together with the table.
    """

    settings = sap.adt.TableSettings(connection, name)
    settings.fetch()

    settings.data_class = dd09l.TABART or ''
    settings.size_category = dd09l.TABKAT or '0'
    settings.buffering.allowed = dd09l.BUFALLOW or 'N'
    settings.buffering.type = dd09l.PUFFERUNG or ''
    settings.buffering.area_key_fields = str(int(dd09l.SCHFELDANZ or '0'))
    settings.logging_enabled = _abap_flag_to_adt(dd09l.PROTOKOLL)

    # abapGit does not write the default values which depend on the release
    if dd09l.ROWORCOLST:
        settings.storage_type = dd09l.ROWORCOLST

    if dd09l.SHARINGTYPE:
        settings.sharing_type = dd09l.SHARINGTYPE

    if dd09l.LOAD_UNIT:
        settings.load_unit = dd09l.LOAD_UNIT

    with settings.open_editor(corrnr=corrnr) as editor:
        editor.push()


def prepare_tabl(repo_obj):
    """Reads and checks the file of the structure or table and generates its
       source code without accessing the system
    """

    with open(repo_obj.path, encoding='utf-8') as abap_data_file:
        try:
            results = sap.platform.abap.abapgit.from_xml(
                [DD02V, sap.platform.abap.abapgit.OptionalBody(DD09L),
                 sap.platform.abap.abapgit.OptionalBody(DD03P_TABLE)],
                abap_data_file.read())
        except sap.errors.SAPCliError as ex:
            # e.g. foreign keys or search helps which are not supported yet
            raise sap.adt.errors.ExceptionCheckinFailure(
                f'Unsupported contents of TABL {repo_obj.name}: {ex}') from ex

    dd02v = results['DD02V']
    fields = results.get('DD03P_TABLE', [])

    if dd02v.TABCLASS == TABCLASS_TRANSPARENT:
        return SimpleNamespace(dd02v=dd02v, dd09l=results.get('DD09L') or DD09L(),
                               source_code=build_table_source(dd02v, fields, repo_obj.name))

    if dd02v.TABCLASS != TABCLASS_STRUCTURE:
        raise sap.adt.errors.ExceptionCheckinFailure(
            f'Unsupported table category "{dd02v.TABCLASS}" of {repo_obj.name}:'
            ' only structures and transparent tables are supported')

    return SimpleNamespace(dd02v=dd02v, dd09l=None, source_code=build_structure_source(dd02v, fields, repo_obj.name))


def checkin_tabl(connection, repo_obj, corrnr=None, check_before_save=False, prepared=None):
    """Checkin ADT Structure or Table"""

    prepared = prepared or prepare_tabl(repo_obj)
    is_table = prepared.dd02v.TABCLASS == TABCLASS_TRANSPARENT
    label = 'Table' if is_table else 'Structure'

    sap.cli.core.printout(f'Creating {label}:', repo_obj.name)

    metadata = sap.adt.ADTCoreData(language='EN', master_language='EN', responsible=connection.user.upper(),
                                   description=prepared.dd02v.DDTEXT)
    adt_type = sap.adt.Table if is_table else sap.adt.Structure
    adt_object = adt_type(connection, repo_obj.name.upper(), package=repo_obj.package.name, metadata=metadata)

    try:
        adt_object.create(corrnr)
    except sap.adt.errors.ExceptionResourceAlreadyExists as err:
        mod_log().info(err.message)

    sap.cli.core.printout(f'Writing {label}:', repo_obj.name)
    sap.fileformat.adt.write_source(prepared.source_code, adt_object, corrnr=corrnr, source_label=repo_obj.path,
                                    check_before_save=check_before_save)

    if is_table:
        sap.cli.core.printout('Writing Technical Settings:', repo_obj.name)
        _write_table_settings(connection, repo_obj.name.upper(), prepared.dd09l, corrnr)

    # Activation of the table activates its technical settings too
    return ObjectCheckinResult([adt_object], [])


def _abap_flag_to_adt(flag):
    """Returns ADT boolean value of the given ABAP flag"""

    return 'true' if flag else 'false'


def prepare_doma(repo_obj):
    """Reads and checks the file of the domain without accessing the system"""

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

    return SimpleNamespace(dd01v=results['DD01V'], dd07v=results.get('DD07V_TAB', []))


# pylint: disable=unused-argument,too-many-locals
def checkin_doma(connection, repo_obj, corrnr=None, check_before_save=False, prepared=None):
    """Checkin ADT Domain"""

    sap.cli.core.printout('Creating Domain:', repo_obj.name)

    prepared = prepared or prepare_doma(repo_obj)
    dd01v = prepared.dd01v

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
    for position, dd07v in enumerate(prepared.dd07v, start=1):
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


def prepare_dtel(repo_obj):
    """Reads and checks the file of the data element without accessing
       the system
    """

    with open(repo_obj.path, encoding='utf-8') as abap_data_file:
        try:
            # DD04L_EXTRA is parsed only to accept files of newer abapGit versions
            results = sap.platform.abap.abapgit.from_xml(
                [DD04V, sap.platform.abap.abapgit.OptionalBody(DD04L_EXTRA)],
                abap_data_file.read())
        except sap.errors.SAPCliError as ex:
            # e.g. translations or long texts which are not supported yet
            raise sap.adt.errors.ExceptionCheckinFailure(
                f'Unsupported contents of data element {repo_obj.name}: {ex}') from ex

    dd04v = results['DD04V']

    if dd04v.REFKIND not in (None, REFKIND_DOMAIN):
        raise sap.adt.errors.ExceptionCheckinFailure(
            f'Unsupported type of data element {repo_obj.name}: REFKIND={dd04v.REFKIND}')

    return SimpleNamespace(dd04v=dd04v)


# pylint: disable=unused-argument
def checkin_dtel(connection, repo_obj, corrnr=None, check_before_save=False, prepared=None):
    """Checkin ADT Data Element"""

    sap.cli.core.printout('Creating Data Element:', repo_obj.name)

    dd04v = (prepared or prepare_dtel(repo_obj)).dd04v

    metadata = sap.adt.ADTCoreData(language='EN', master_language='EN', responsible=connection.user.upper(),
                                   description=dd04v.DDTEXT)
    dataelement = sap.adt.DataElement(connection, repo_obj.name.upper(), package=repo_obj.package.name,
                                      metadata=metadata)

    try:
        dataelement.create(corrnr)
    except sap.adt.errors.ExceptionResourceAlreadyExists as err:
        mod_log().info(err.message)

    dataelement.fetch()
    dataelement.description = dd04v.DDTEXT

    definition = dataelement.definition
    # DDIC accepts data elements with the domain name but without
    # REFKIND which abapGit passes through without any changes
    if dd04v.REFKIND == REFKIND_DOMAIN or dd04v.DOMNAME:
        definition.typ = 'domain'
        definition.typ_name = dd04v.DOMNAME
        definition.data_type = ''
        definition.data_type_length = '0'
        definition.data_type_decimals = '0'
    else:
        definition.typ = 'predefinedAbapType'
        definition.typ_name = ''
        # ADT does not accept DDIC names of data types of data elements
        definition.data_type = DDIC_DATATYPE_TO_ADT.get(dd04v.DATATYPE, dd04v.DATATYPE)
        definition.data_type_length = dd04v.LENG or '0'
        definition.data_type_decimals = dd04v.DECIMALS or '0'

    definition.label_short = dd04v.SCRTEXT_S or ''
    definition.label_short_length = dd04v.SCRLEN1 or '0'
    definition.label_medium = dd04v.SCRTEXT_M or ''
    definition.label_medium_length = dd04v.SCRLEN2 or '0'
    definition.label_long = dd04v.SCRTEXT_L or ''
    definition.label_long_length = dd04v.SCRLEN3 or '0'
    definition.label_heading = dd04v.REPTEXT or ''
    definition.label_heading_length = dd04v.HEADLEN or '0'
    definition.search_help = dd04v.SHLPNAME or ''
    definition.search_help_parameter = dd04v.SHLPFIELD or ''
    definition.set_get_parameter = dd04v.MEMORYID or ''
    definition.default_component_name = dd04v.DEFFDNAME or ''
    definition.deactivate_input_history = _abap_flag_to_adt(dd04v.NOHISTORY)
    definition.change_document = _abap_flag_to_adt(dd04v.LOGFLAG)
    definition.left_to_right_direction = _abap_flag_to_adt(dd04v.LTRFLDDIS)
    definition.deactivate_bidi_filtering = _abap_flag_to_adt(dd04v.BIDICTRLC)

    sap.cli.core.printout('Writing Data Element:', repo_obj.name)
    with dataelement.open_editor(corrnr=corrnr) as editor:
        editor.push()

    return ObjectCheckinResult([dataelement], [])


OBJECT_CHECKIN_HANDLERS = {
    'bdef': checkin_bdef,
    'tabl': checkin_tabl,
    'doma': checkin_doma,
    'dtel': checkin_dtel,
}


# Functions reading and checking the files of objects without accessing
# the system
OBJECT_CHECKIN_PREPARERS = {
    'bdef': prepare_bdef,
    'tabl': prepare_tabl,
    'doma': prepare_doma,
    'dtel': prepare_dtel,
}


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
            context = CheckinContext(connection, repo_obj.package.name, corrnr, check_before_save)
            result = handler.checkin(context, repo_obj, prepared_obj)
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
