"""Structures and transparent tables in the abapGit serialization

   abapGit stores the DDIC definition and ADT works with DDL source code, so
   the handler generates the source code on checkin and parses it on checkout.
"""

import re
from types import SimpleNamespace

from sap import get_logger

import sap.adt
import sap.adt.errors
import sap.errors
import sap.adt.checks
import sap.platform.abap.abapgit
from sap.platform.abap.localrepository import ObjectHandler, ObjectCheckinResult
from sap.platform.abap.abapgit.ddic import ddic_number, adt_flag_to_abap, abap_flag_to_adt
from sap.platform.abap.abapgit.files import dump_attributes_to_file
from sap.platform.abap.ddic import DD02V, DD03P, DD03P_TABLE, DD09L, TABCLASS_STRUCTURE, TABCLASS_TRANSPARENT, \
    DD02V_EXCLASS_TO_DDL, DD02V_MAINFLAG_TO_DDL, DDIC_DATATYPE_TO_DDL
from sap.platform.language import iso_code_to_sap_code


def mod_log():
    """Module logger"""

    return get_logger()


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
            raise sap.errors.SAPCliError('unexpected end of source code')

        return self._tokens[self._index]

    def _next(self):
        token = self._peek()
        self._index += 1
        return token

    def _expect(self, expected):
        token = self._next()
        if token.lower() != expected:
            raise sap.errors.SAPCliError(f'unexpected token "{token}"')

    def _annotations(self, supported):
        annotations = {}

        while self._peek().startswith('@'):
            name = self._next()
            if name.lower() not in supported:
                raise sap.errors.SAPCliError(f'unsupported annotation {name}')

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
            raise sap.errors.SAPCliError(f'unsupported data type {type_name}') from ex

        if len(params) != param_count:
            raise sap.errors.SAPCliError(f'invalid parameters of data type {type_name}')

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
                raise sap.errors.SAPCliError('unsupported key include')

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
            raise sap.errors.SAPCliError(f'unexpected token "{self._tokens[self._index]}"')

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
        raise sap.errors.SAPCliError(f'unsupported {label} {value}') from ex


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


def checkout_structure(connection, name, observer, destdir=None):
    """Download structure attributes"""

    observer.checking_out(name)
    adt_structure = sap.adt.Structure(connection, name)
    adt_structure.fetch()

    try:
        abap_attributes = build_structure_abap_attributes(adt_structure, adt_structure.text)
    except sap.errors.SAPCliError as ex:
        raise sap.errors.SAPCliError(f'Checkout of structure {name} failed: {ex}')

    dump_attributes_to_file(observer, name, abap_attributes, '.tabl', 'LCL_OBJECT_TABL', destdir=destdir)


def build_table_abap_attributes(adt_table, source, settings):
    """Returns populated ABAP structures with attributes"""

    annotations, fields = StructureSourceParser(source, kind='table').parse()

    table_category = annotations.get('@abapcatalog.tablecategory')
    if table_category is None or table_category.upper() != '#TRANSPARENT':
        raise sap.errors.SAPCliError(f'unsupported table category {table_category}')

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


def checkout_table(connection, name, observer, destdir=None):
    """Download table attributes"""

    observer.checking_out(name)
    adt_table = sap.adt.Table(connection, name)
    adt_table.fetch()
    source = adt_table.text

    settings = sap.adt.TableSettings(connection, name)
    settings.fetch()

    try:
        abap_attributes = build_table_abap_attributes(adt_table, source, settings)
    except sap.errors.SAPCliError as ex:
        raise sap.errors.SAPCliError(f'Checkout of table {name} failed: {ex}')

    dump_attributes_to_file(observer, name, abap_attributes, '.tabl', 'LCL_OBJECT_TABL', destdir=destdir)


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
    settings.logging_enabled = abap_flag_to_adt(dd09l.PROTOKOLL)

    # abapGit does not write the default values which depend on the release
    if dd09l.ROWORCOLST:
        settings.storage_type = dd09l.ROWORCOLST

    if dd09l.SHARINGTYPE:
        settings.sharing_type = dd09l.SHARINGTYPE

    if dd09l.LOAD_UNIT:
        settings.load_unit = dd09l.LOAD_UNIT

    with settings.open_editor(corrnr=corrnr) as editor:
        editor.push()


class TableHandler(ObjectHandler):
    """Structure or transparent table: <name>.tabl.xml"""

    FILE_TYPE = 'tabl'
    METADATA_EXT = 'xml'
    ADT_TYPES = ('TABL/DT', 'TABL/DS')

    def checkout(self, connection, adt_type, name, destdir, observer):
        if adt_type == sap.adt.Table.OBJTYPE.code:
            checkout_table(connection, name, observer, destdir=destdir)
        else:
            checkout_structure(connection, name, observer, destdir=destdir)

    def prepare(self, repo_obj, observer):
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

    def checkin(self, context, repo_obj, prepared):
        is_table = prepared.dd02v.TABCLASS == TABCLASS_TRANSPARENT
        label = 'Table' if is_table else 'Structure'

        context.observer.creating(label, repo_obj.name)

        metadata = sap.adt.ADTCoreData(language='EN', master_language='EN', responsible=context.connection.user.upper(),
                                       description=prepared.dd02v.DDTEXT)
        adt_type = sap.adt.Table if is_table else sap.adt.Structure
        adt_object = adt_type(context.connection, repo_obj.name.upper(), package=context.package_name, metadata=metadata)

        try:
            adt_object.create(context.corrnr)
        except sap.adt.errors.ExceptionResourceAlreadyExists as err:
            mod_log().info(err.message)

        context.observer.writing(label, repo_obj.name)
        sap.adt.checks.write_source(prepared.source_code, adt_object, corrnr=context.corrnr, source_label=repo_obj.path,
                                    check_before_save=context.check_before_save)

        if is_table:
            context.observer.writing('Technical Settings', repo_obj.name)
            _write_table_settings(context.connection, repo_obj.name.upper(), prepared.dd09l, context.corrnr)

        # Activation of the table activates its technical settings too
        return ObjectCheckinResult([adt_object], [])

    def locate(self, repo_obj, part, line):
        # The source code of structures and tables is generated from the XML file
        return None
