"""Table types in the abapGit serialization"""

from types import SimpleNamespace

from sap import get_logger

import sap.adt
import sap.adt.errors
import sap.errors
import sap.platform.abap.abapgit
from sap.platform.abap.localrepository import ObjectHandler, ObjectCheckinResult, UnsupportedContent
from sap.platform.abap.abapgit.ddic import ADT_TO_DDIC_DATATYPE, ddic_number
from sap.platform.abap.abapgit.files import dump_attributes_to_file
from sap.platform.abap.ddic import DD40V, DD42V, DD42V_TABLE, DD43V_TABLE, DD40L_EXTRA, DD40V_ACCESSMODE_TO_ADT, \
    DD40V_KEYDEF_TO_ADT, DD40V_KEYKIND_TO_ADT
from sap.platform.language import iso_code_to_sap_code

ADT_TO_DD40V_ACCESSMODE = {adt: code for code, adt in DD40V_ACCESSMODE_TO_ADT.items()}
ADT_TO_DD40V_KEYDEF = {adt: code for code, adt in DD40V_KEYDEF_TO_ADT.items()}
ADT_TO_DD40V_KEYKIND = {adt: code for code, adt in DD40V_KEYKIND_TO_ADT.items()}


def mod_log():
    """Module logger"""

    return get_logger()


def build_table_type_abap_attributes(adt_tabletype):
    """Returns populated ABAP structures with attributes"""

    row_type = adt_tabletype.row_type
    if row_type.type_kind not in ('dictionaryType', 'predefinedAbapType'):
        raise sap.errors.SAPCliError(f'unsupported row type kind {row_type.type_kind}')

    data_type = row_type.built_in_type.data_type
    data_type = ADT_TO_DDIC_DATATYPE.get(data_type, data_type)

    components = [component.name for component in adt_tabletype.primary_key.components]

    dd40v = DD40V()
    dd40v.TYPENAME = adt_tabletype.name
    dd40v.DDLANGUAGE = iso_code_to_sap_code(adt_tabletype.master_language)

    if row_type.type_kind == 'dictionaryType':
        dd40v.ROWTYPE = row_type.type_name
        dd40v.ROWKIND = {'STRU': 'S', 'TTYP': 'L'}.get(data_type, 'E')

    dd40v.DATATYPE = data_type
    dd40v.LENG = ddic_number(row_type.built_in_type.length, 6)
    dd40v.DECIMALS = ddic_number(row_type.built_in_type.decimals, 6)
    dd40v.ACCESSMODE = ADT_TO_DD40V_ACCESSMODE[adt_tabletype.access_type]
    dd40v.KEYDEF = ADT_TO_DD40V_KEYDEF[adt_tabletype.primary_key.definition]
    dd40v.KEYKIND = ADT_TO_DD40V_KEYKIND[adt_tabletype.primary_key.kind]
    dd40v.KEYFDCOUNT = ddic_number(len(components), 4)
    dd40v.DDTEXT = adt_tabletype.description

    if not components:
        return (dd40v,)

    # ADT does not provide ROWTYPEPOS - the position of the component in the row type
    dd42v = DD42V_TABLE()
    for position, component in enumerate(components, start=1):
        dd42v.append(DD42V(TYPENAME=adt_tabletype.name, KEYFDPOS=f'{position:04d}', KEYFIELD=component))

    return (dd40v, dd42v)


def _dd40v_code_to_adt(mapping, dd40v, field, object_name):
    """Returns ADT value of the given DD40V field"""

    code = getattr(dd40v, field)
    try:
        return mapping[code]
    except KeyError as ex:
        raise sap.adt.errors.ExceptionCheckinFailure(
            f'Unsupported {field} "{code}" of table type {object_name}') from ex


class TableTypeHandler(ObjectHandler):
    """Table type: <name>.ttyp.xml"""

    FILE_TYPE = 'ttyp'
    METADATA_EXT = 'xml'
    ADT_TYPES = ('TTYP/DA',)

    def checkout(self, connection, adt_type, name, destdir, observer):
        observer.checking_out(name)
        adt_tabletype = sap.adt.TableType(connection, name)
        adt_tabletype.fetch()

        try:
            abap_attributes = build_table_type_abap_attributes(adt_tabletype)
        except sap.errors.SAPCliError as ex:
            raise UnsupportedContent(f'Checkout of table type {name} failed: {ex}') from ex

        if adt_tabletype.secondary_keys.keys:
            observer.warning(f'Skipping unsupported secondary keys of {name}')

        dump_attributes_to_file(observer, name, abap_attributes, '.ttyp', 'LCL_OBJECT_TTYP', destdir=destdir)

    def prepare(self, repo_obj, observer):
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

        if results.get('DD43V'):
            observer.warning(f'Skipping unsupported secondary keys of {repo_obj.name}')

        return SimpleNamespace(
            dd40v=dd40v,
            access_type=_dd40v_code_to_adt(DD40V_ACCESSMODE_TO_ADT, dd40v, 'ACCESSMODE', repo_obj.name),
            key_definition=_dd40v_code_to_adt(DD40V_KEYDEF_TO_ADT, dd40v, 'KEYDEF', repo_obj.name),
            key_kind=_dd40v_code_to_adt(DD40V_KEYKIND_TO_ADT, dd40v, 'KEYKIND', repo_obj.name),
            key_components=[line.KEYFIELD for line in results.get('DD42V', []) if not line.SECKEYNAME])

    def checkin(self, context, repo_obj, prepared):
        context.observer.creating('Table Type', repo_obj.name)

        dd40v = prepared.dd40v

        metadata = sap.adt.ADTCoreData(language='EN', master_language='EN', responsible=context.connection.user.upper(),
                                       description=dd40v.DDTEXT)
        tabletype = sap.adt.TableType(context.connection, repo_obj.name.upper(), package=context.package_name,
                                      metadata=metadata)

        try:
            tabletype.create(context.corrnr)
        except sap.adt.errors.ExceptionResourceAlreadyExists as err:
            mod_log().info(err.message)

        # ADT fills in the definition defaults on creation
        tabletype.fetch()

        if dd40v.ROWKIND:
            tabletype.set_dictionary_row_type(dd40v.ROWTYPE)
        else:
            tabletype.set_predefined_row_type(dd40v.DATATYPE, dd40v.LENG or '0', dd40v.DECIMALS or '0')

        tabletype.access_type = prepared.access_type
        tabletype.set_primary_key(prepared.key_definition, prepared.key_kind, prepared.key_components)

        context.observer.writing('Table Type', repo_obj.name)
        with tabletype.open_editor(corrnr=context.corrnr) as editor:
            editor.push()

        return ObjectCheckinResult([tabletype], [])

    def locate(self, repo_obj, part, line):
        # Table types have no source code
        return None
