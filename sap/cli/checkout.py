# pylint: disable=too-many-lines
"""ADT Object export"""
import os
import re
import sys

import sap.adt
import sap.adt.textelements
import sap.cli.core

from sap.platform.abap.ddic import (
    DEVC,
    DD02V,
    DD03P,
    DD03P_TABLE,
    TABCLASS_STRUCTURE,
    DD02V_EXCLASS_TO_DDL,
    DDIC_DATATYPE_TO_DDL,
    TABCLASS_TRANSPARENT,
    DD02V_MAINFLAG_TO_DDL,
    DD09L,
)
from sap.platform.language import iso_code_to_sap_code

from sap.platform.abap.abapgit import DOT_ABAP_GIT

import sap.fileformat.abapgit
from sap.fileformat import HandlerRegistry
from sap.fileformat.abapgit.fugr import SourceCodeFormat, checkout_function_group
from sap.fileformat.abapgit.ddic import ddic_number, adt_flag_to_abap
from sap.fileformat.abapgit.files import dump_attributes_to_file

# Handlers of the object types already migrated to sap.fileformat
OBJECT_HANDLERS = HandlerRegistry(sap.fileformat.abapgit.HANDLERS)


class CommandGroup(sap.cli.core.CommandGroup):
    """Commands for exporting ADT objects"""

    def __init__(self):
        super().__init__('checkout')


def _checkout_object(connection, adt_type, name):
    """Checks out the object to the current directory"""

    OBJECT_HANDLERS.for_adt_type(adt_type).checkout(connection, adt_type, name.upper(), None)


@CommandGroup.argument('name')
@CommandGroup.command('class')
def abapclass(connection, args):
    """Download all class sources command wrapper"""

    _checkout_object(connection, sap.adt.Class.OBJTYPE.code, args.name)


@CommandGroup.argument('name')
@CommandGroup.command()
def program(connection, args):
    """Download program sources command wrapper"""

    _checkout_object(connection, sap.adt.Program.OBJTYPE.code, args.name)


@CommandGroup.argument('name')
@CommandGroup.command()
def interface(connection, args):
    """Download interface sources command wrapper"""

    _checkout_object(connection, sap.adt.Interface.OBJTYPE.code, args.name)


@CommandGroup.argument('-f', '--format', type=str,
                       choices=[SourceCodeFormat.ABAP.value, SourceCodeFormat.ABAPGIT.value],
                       default=SourceCodeFormat.ABAPGIT.value)
@CommandGroup.argument('name')
@CommandGroup.command()
def function_group(connection, args):
    """Download function group sources command wrapper"""

    try:
        checkout_function_group(connection, args.name.upper(), source_format=SourceCodeFormat(args.format))
    except sap.cli.core.SAPCliError as ex:
        sap.cli.core.printerr(f'Checkout failed: {str(ex)}')
        return 1

    return 0


@CommandGroup.argument('name')
@CommandGroup.command()
def tabletype(connection, args):
    """Download table type attributes command wrapper"""

    _checkout_object(connection, sap.adt.TableType.OBJTYPE.code, args.name)


@CommandGroup.argument('name')
@CommandGroup.command('ddl')
def datadefinition(connection, args):
    """Download data definition source code and attributes command wrapper"""

    _checkout_object(connection, sap.adt.DataDefinition.OBJTYPE.code, args.name)


@CommandGroup.argument('name')
@CommandGroup.command('dcl')
def accesscontrol(connection, args):
    """Download access control source code and attributes command wrapper"""

    _checkout_object(connection, sap.adt.AccessControl.OBJTYPE.code, args.name)


@CommandGroup.argument('name')
@CommandGroup.command('ddlx')
def metadataextension(connection, args):
    """Download metadata extension source code and attributes command wrapper"""

    _checkout_object(connection, sap.adt.MetadataExtension.OBJTYPE.code, args.name)


@CommandGroup.argument('name')
@CommandGroup.command('bdef')
def behaviordefinition(connection, args):
    """Download behavior definition source code and attributes command wrapper"""

    _checkout_object(connection, sap.adt.BehaviorDefinition.OBJTYPE.code, args.name)


DDL_TO_DD02V_EXCLASS = {ddl: code for code, ddl in DD02V_EXCLASS_TO_DDL.items()}
DDL_TO_DD02V_MAINFLAG = {ddl: code for code, ddl in DD02V_MAINFLAG_TO_DDL.items()}
DDL_TO_DDIC_DATATYPE = {ddl: (ddic, params) for ddic, (ddl, params) in DDIC_DATATYPE_TO_DDL.items()}

# DDIC lengths and decimals of the DDIC built-in data types without DDL parameters
DDIC_DATATYPE_FIXED_LENGTH = {
    'INT1': ('3', '0'),
    'INT2': ('5', '0'),
    'INT4': ('10', '0'),
    'INT8': ('19', '0'),
    'FLTP': ('16', '16'),
    'CUKY': ('5', '0'),
    'DATS': ('8', '0'),
    'TIMS': ('6', '0'),
    'CLNT': ('3', '0'),
    'LANG': ('1', '0'),
    'ACCP': ('6', '0'),
}

# ABAP internal types of DDIC built-in data types and their lengths in bytes
# computed from the DDIC lengths - checkout does not write them for the
# types which are not listed here
DDIC_DATATYPE_INTERNAL_TYPE = {
    'CHAR': ('C', lambda length: length * 2),
    'NUMC': ('N', lambda length: length * 2),
    'RAW': ('X', lambda length: length),
    'LRAW': ('X', lambda length: length),
    'LCHR': ('C', lambda length: length * 2),
    'STRG': ('g', lambda length: 8),
    'UNIT': ('C', lambda length: length * 2),
    'DEC': ('P', lambda length: (length + 2) // 2),
    'CURR': ('P', lambda length: (length + 2) // 2),
    'QUAN': ('P', lambda length: (length + 2) // 2),
    'INT1': ('X', lambda length: 1),
    'INT2': ('X', lambda length: 2),
    'INT4': ('X', lambda length: 4),
    'INT8': ('8', lambda length: 8),
    'FLTP': ('F', lambda length: 8),
    'CUKY': ('C', lambda length: length * 2),
    'DATS': ('D', lambda length: length * 2),
    'TIMS': ('T', lambda length: length * 2),
    'CLNT': ('C', lambda length: length * 2),
    'LANG': ('C', lambda length: length * 2),
    'ACCP': ('N', lambda length: length * 2),
}

# Tokens of DDL source code - comments are matched to be skipped
DDL_TOKENS = re.compile(r"""(?P<comment>//[^\n]*|--[^\n]*|/\*.*?\*/)"""
                        r"""|(?P<token>'(?:[^']|'')*'|"[^"]*"|[{}():;,]|[^\s{}():;,'"]+)""", re.DOTALL)


def _ddl_unquote(token):
    """Returns the value of the DDL string literal or delimited name"""

    if token[:1] in ('"', "'"):
        return token[1:-1].replace("''", "'")

    return token


# Supported header annotations of DDL source code of structures and tables
DDL_HEADER_ANNOTATIONS = {
    'structure': ('@endusertext.label', '@abapcatalog.enhancement.category'),
    'table': ('@endusertext.label', '@abapcatalog.enhancement.category', '@abapcatalog.tablecategory',
              '@abapcatalog.deliveryclass', '@abapcatalog.datamaintenance'),
}


class StructureSourceParser:
    """Parser of DDL source code of structures and tables"""

    def __init__(self, source, kind='structure'):
        self._tokens = [match.group('token') for match in DDL_TOKENS.finditer(source) if match.group('token')]
        self._index = 0
        self._kind = kind

    def _peek(self):
        if self._index >= len(self._tokens):
            raise sap.cli.core.SAPCliError('unexpected end of source code')

        return self._tokens[self._index]

    def _next(self):
        token = self._peek()
        self._index += 1
        return token

    def _expect(self, expected):
        token = self._next()
        if token.lower() != expected:
            raise sap.cli.core.SAPCliError(f'unexpected token "{token}"')

    def _annotations(self, supported):
        annotations = {}

        while self._peek().startswith('@'):
            name = self._next()
            if name.lower() not in supported:
                raise sap.cli.core.SAPCliError(f'unsupported annotation {name}')

            self._expect(':')
            annotations[name.lower()] = self._next()

        return annotations

    def _include(self, field):
        field.FIELDNAME = '.INCLUDE'
        field.PRECFIELD = self._next().upper()

        if self._peek().lower() == 'with':
            self._next()
            self._expect('suffix')
            field.FIELDNAME = f'.INCLU-{self._next().upper()}'

        field.MASK = '      S'
        field.COMPTYPE = 'S'

    def _type(self, field):
        type_name = self._next()
        if not type_name.lower().startswith('abap.'):
            field.ROLLNAME = type_name.upper()
            # database tables cannot have components typed by structures
            # or table types
            if self._kind == 'table':
                field.COMPTYPE = 'E'

            return

        params = []
        if self._peek() == '(':
            self._next()
            params.append(self._next())
            if self._peek() == ',':
                self._next()
                params.append(self._next())
            self._expect(')')

        try:
            datatype, param_count = DDL_TO_DDIC_DATATYPE[type_name.lower()[5:]]
        except KeyError as ex:
            raise sap.cli.core.SAPCliError(f'unsupported data type {type_name}') from ex

        if len(params) != param_count:
            raise sap.cli.core.SAPCliError(f'invalid parameters of data type {type_name}')

        length, decimals = (params + ['0', '0'])[:2] if param_count else DDIC_DATATYPE_FIXED_LENGTH[datatype]

        if datatype in DDIC_DATATYPE_INTERNAL_TYPE:
            inttype, intlen = DDIC_DATATYPE_INTERNAL_TYPE[datatype]
            field.INTTYPE = inttype
            field.INTLEN = ddic_number(intlen(int(length)), 6)

        field.DATATYPE = datatype
        field.LENG = ddic_number(length, 6)
        field.DECIMALS = ddic_number(decimals, 6)
        field.MASK = f'  {datatype}'

    def _field(self):
        annotations = self._annotations(('@endusertext.label', '@semantics.amount.currencycode',
                                         '@semantics.quantity.unitofmeasure'))

        # The values are set in the order of the members to keep the order
        # of XML elements
        field = DD03P()
        field.ADMINFIELD = '0'

        name = self._next()
        # the field can be named key
        if self._kind == 'table' and name.lower() == 'key' and self._peek() != ':':
            field.KEYFLAG = 'X'
            name = self._next()
            if name.lower() == 'include':
                raise sap.cli.core.SAPCliError('unsupported key include')

        if name.lower() == 'include':
            self._include(field)
        else:
            self._expect(':')
            if self._peek().lower() == 'include':
                self._next()
                field.GROUPNAME = _ddl_unquote(name).upper()
                self._include(field)
            else:
                field.FIELDNAME = _ddl_unquote(name).upper()
                self._type(field)

        if self._kind == 'table' and self._peek().lower() == 'not':
            self._next()
            self._expect('null')
            field.NOTNULL = 'X'

        self._expect(';')

        if '@endusertext.label' in annotations:
            field.DDTEXT = _ddl_unquote(annotations['@endusertext.label'])

        reference = annotations.get('@semantics.amount.currencycode',
                                    annotations.get('@semantics.quantity.unitofmeasure'))
        if reference:
            field.REFTABLE, _, field.REFFIELD = _ddl_unquote(reference).upper().partition('.')

        return field

    def parse(self):
        """Returns the header annotations and the fields"""

        annotations = self._annotations(DDL_HEADER_ANNOTATIONS[self._kind])

        self._expect('define')
        self._expect(self._kind)
        self._next()
        self._expect('{')

        fields = DD03P_TABLE()
        while self._peek() != '}':
            fields.append(self._field())

        self._next()
        if self._index < len(self._tokens):
            raise sap.cli.core.SAPCliError(f'unexpected token "{self._tokens[self._index]}"')

        return (annotations, fields)


def _ddl_annotation_to_code(annotations, name, mapping, label):
    """Returns the DDIC code of the DDL value of the given annotation or None
       if the annotation is not present.
    """

    value = annotations.get(name)
    if value is None:
        return None

    try:
        return mapping[value.upper()]
    except KeyError as ex:
        raise sap.cli.core.SAPCliError(f'unsupported {label} {value}') from ex


def build_structure_abap_attributes(adt_structure, source):
    """Returns populated ABAP structures with attributes"""

    annotations, fields = StructureSourceParser(source).parse()
    exclass = _ddl_annotation_to_code(annotations, '@abapcatalog.enhancement.category', DDL_TO_DD02V_EXCLASS,
                                      'enhancement category')

    dd02v = DD02V()
    dd02v.TABNAME = adt_structure.name
    dd02v.DDLANGUAGE = iso_code_to_sap_code(adt_structure.master_language)
    dd02v.TABCLASS = TABCLASS_STRUCTURE
    dd02v.DDTEXT = adt_structure.description
    dd02v.MASTERLANG = iso_code_to_sap_code(adt_structure.master_language)
    dd02v.EXCLASS = exclass

    return (dd02v, fields)


def checkout_structure(connection, name, destdir=None):
    """Download structure attributes"""

    sap.cli.core.printout(name)
    adt_structure = sap.adt.Structure(connection, name)
    adt_structure.fetch()

    try:
        abap_attributes = build_structure_abap_attributes(adt_structure, adt_structure.text)
    except sap.cli.core.SAPCliError as ex:
        raise sap.cli.core.SAPCliError(f'Checkout of structure {name} failed: {ex}')

    dump_attributes_to_file(name, abap_attributes, '.tabl', 'LCL_OBJECT_TABL', destdir=destdir)


def build_table_abap_attributes(adt_table, source, settings):
    """Returns populated ABAP structures with attributes"""

    annotations, fields = StructureSourceParser(source, kind='table').parse()

    table_category = annotations.get('@abapcatalog.tablecategory')
    if table_category is None or table_category.upper() != '#TRANSPARENT':
        raise sap.cli.core.SAPCliError(f'unsupported table category {table_category}')

    language = iso_code_to_sap_code(adt_table.master_language)

    # The values are set in the order of the members to keep the order
    # of XML elements
    dd02v = DD02V()
    dd02v.TABNAME = adt_table.name
    dd02v.DDLANGUAGE = language
    dd02v.TABCLASS = TABCLASS_TRANSPARENT
    dd02v.DDTEXT = adt_table.description
    dd02v.MASTERLANG = language
    # abapGit does not write initial values
    dd02v.MAINFLAG = _ddl_annotation_to_code(annotations, '@abapcatalog.datamaintenance', DDL_TO_DD02V_MAINFLAG,
                                             'data maintenance') or None
    delivery_class = annotations.get('@abapcatalog.deliveryclass')
    dd02v.CONTFLAG = delivery_class.lstrip('#').upper() if delivery_class else None
    dd02v.EXCLASS = _ddl_annotation_to_code(annotations, '@abapcatalog.enhancement.category', DDL_TO_DD02V_EXCLASS,
                                            'enhancement category')

    dd09l = DD09L()
    dd09l.TABNAME = adt_table.name
    dd09l.AS4LOCAL = 'A'
    dd09l.TABKAT = settings.size_category
    dd09l.TABART = settings.data_class
    dd09l.PUFFERUNG = settings.buffering.type or None
    dd09l.SCHFELDANZ = ddic_number(settings.buffering.area_key_fields, 3)
    dd09l.PROTOKOLL = adt_flag_to_abap(settings.logging_enabled)
    dd09l.BUFALLOW = settings.buffering.allowed or None
    # abapGit does not write the column store because it is the default value
    dd09l.ROWORCOLST = settings.storage_type if settings.storage_type not in ('', 'C') else None
    dd09l.SHARINGTYPE = settings.sharing_type or None
    dd09l.LOAD_UNIT = settings.load_unit or None

    return (dd02v, dd09l, fields)


def checkout_table(connection, name, destdir=None):
    """Download table attributes"""

    sap.cli.core.printout(name)
    adt_table = sap.adt.Table(connection, name)
    adt_table.fetch()
    source = adt_table.text

    settings = sap.adt.TableSettings(connection, name)
    settings.fetch()

    try:
        abap_attributes = build_table_abap_attributes(adt_table, source, settings)
    except sap.cli.core.SAPCliError as ex:
        raise sap.cli.core.SAPCliError(f'Checkout of table {name} failed: {ex}')

    dump_attributes_to_file(name, abap_attributes, '.tabl', 'LCL_OBJECT_TABL', destdir=destdir)


@CommandGroup.argument('name')
@CommandGroup.command()
def table(connection, args):
    """Download table attributes command wrapper"""

    checkout_table(connection, args.name.upper())


@CommandGroup.argument('name')
@CommandGroup.command()
def structure(connection, args):
    """Download structure attributes command wrapper"""

    checkout_structure(connection, args.name.upper())


@CommandGroup.argument('name')
@CommandGroup.command()
def domain(connection, args):
    """Download domain attributes command wrapper"""

    _checkout_object(connection, sap.adt.Domain.OBJTYPE.code, args.name)


@CommandGroup.argument('name')
@CommandGroup.command()
def dataelement(connection, args):
    """Download data element attributes command wrapper"""

    _checkout_object(connection, sap.adt.DataElement.OBJTYPE.code, args.name)


def checkout_objects(connection, objects, destdir=None):
    """Checkout all objects from the give list"""

    # This could be a global variable but it breaks mock patching in tests
    #
    # The checkout function shall return None and errors should be reported by
    # raising an SAPCliError because the command handler prints out
    # human friendly text.
    checkouters = {
        sap.adt.Structure.OBJTYPE.code: checkout_structure,
        sap.adt.Table.OBJTYPE.code: checkout_table,
    }

    if not os.path.isdir(destdir):
        os.makedirs(destdir)

    for obj in objects:
        handler = OBJECT_HANDLERS.for_adt_type(obj.typ)
        if handler is not None:
            handler.checkout(connection, obj.typ, obj.name, destdir)
            continue

        try:
            checkouters[obj.typ](connection, obj.name, destdir)
        except KeyError:
            print(f'Unsupported object: {obj.typ} {obj.name}', file=sys.stderr)


def make_repo_dir_for_package(args):
    """Creates and populates the directory to checkout the package into."""

    repo_dir = args.directory
    if not repo_dir:
        repo_dir = args.name

    repo_dir = os.path.abspath(repo_dir)

    if not os.path.isdir(repo_dir):
        os.makedirs(repo_dir)

    dot_abapgit = DOT_ABAP_GIT.for_new_repo(STARTING_FOLDER='/' + args.starting_folder + '/')

    repo_file = os.path.join(repo_dir, '.abapgit.xml')
    with open(repo_file, 'w', encoding='utf8') as dest:
        sap.platform.abap.to_xml(dot_abapgit, dest=dest, top_element='DATA')

    return repo_dir


def build_package_abap_attributes(adt_package):
    """Returns populated ABAP structure with attributes"""

    return DEVC(CTEXT=adt_package.description)


def checkout_package(connection, name, destdir=None):
    """Creates ABAP Package files"""

    adt_package = sap.adt.Package(connection, name)
    adt_package.fetch()

    devc = build_package_abap_attributes(adt_package)
    dump_attributes_to_file('package', (devc,), '.devc', 'LCL_OBJECT_DEVC', destdir=destdir)


# @CommandGroup.argument('--folder-logic', choices=['full', 'prefix'], default='prefix')
@CommandGroup.argument('--recursive', action='store_true', default=False)
@CommandGroup.argument('--starting-folder', default='src')
@CommandGroup.argument('directory', nargs='?', default=None,
                       help='To checkout the package into it; default=<PACKAGE NAME>')
@CommandGroup.argument('name')
@CommandGroup.command()
def package(connection, args):
    """Download sources of objects from the given ABAP package"""

    repo_dir = make_repo_dir_for_package(args)
    source_code_dir = os.path.join(repo_dir, args.starting_folder)

    explored = sap.adt.Package(connection, args.name)

    for package_name_hier, _, objects in sap.adt.package.walk(explored):
        destdir = os.path.abspath(source_code_dir)

        if len(package_name_hier) == 1:
            destdir = os.path.join(destdir, package_name_hier[0].lower())
        elif len(package_name_hier) > 1:
            hier_path = os.path.join(*package_name_hier)
            destdir = os.path.join(destdir, hier_path.lower())

        if not package_name_hier:
            package_name = args.name
        else:
            package_name = package_name_hier[-1]

        checkout_objects(connection, objects, destdir=destdir)
        checkout_package(connection, package_name.upper(), destdir=destdir)

        if not args.recursive:
            break
