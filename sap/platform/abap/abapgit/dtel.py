"""Data elements in the abapGit serialization"""

from types import SimpleNamespace

from sap import get_logger

import sap.adt
import sap.adt.errors
import sap.cli.core
import sap.errors
import sap.platform.abap.abapgit
from sap.platform.abap.localrepository import ObjectHandler, ObjectCheckinResult
from sap.platform.abap.abapgit.ddic import ADT_TO_DDIC_DATATYPE, ddic_number, adt_flag_to_abap, abap_flag_to_adt
from sap.platform.abap.abapgit.files import dump_attributes_to_file
from sap.platform.abap.ddic import DD04V, DD04L_EXTRA, REFKIND_DOMAIN, DDIC_DATATYPE_TO_ADT
from sap.platform.language import iso_code_to_sap_code


def mod_log():
    """Module logger"""

    return get_logger()


# DDIC output lengths of the DDIC built-in data types which do not depend on
# the length - DDIC does not compute output lengths of strings
DDIC_DATATYPE_FIXED_OUTPUT_LENGTH = {
    'INT1': 3,
    'INT2': 6,
    'INT4': 11,
    'INT8': 20,
    'FLTP': 22,
    'DATS': 10,
    'TIMS': 8,
    'LANG': 2,
    'UTCL': 30,
    'D16N': 24,
    'D34N': 46,
    'STRG': 0,
    'RSTR': 0,
    'SSTR': 0,
}


# DDIC built-in data types whose output length is the length
DDIC_DATATYPE_OUTPUT_LENGTH_IS_LENGTH = ('CHAR', 'NUMC', 'CLNT', 'CUKY', 'UNIT', 'ACCP', 'LCHR', 'LRAW')


# DDIC built-in data types of packed numbers
DDIC_DATATYPE_PACKED = ('DEC', 'CURR', 'QUAN')


def ddic_output_length(datatype, length, decimals):
    """Returns the output length DDIC computes for the given built-in data type
       or None if the computation is not known - ADT does not provide it.
    """

    if datatype in DDIC_DATATYPE_FIXED_OUTPUT_LENGTH:
        return DDIC_DATATYPE_FIXED_OUTPUT_LENGTH[datatype]

    length = int(length or '0')

    if datatype in DDIC_DATATYPE_OUTPUT_LENGTH_IS_LENGTH:
        return length

    if datatype == 'RAW':
        return length * 2

    if datatype in DDIC_DATATYPE_PACKED:
        decimals = int(decimals or '0')
        # The integer part has at least one digit (0.25) and a thousands
        # separator after every 3 digits. The fraction has a decimal point.
        integer_digits = max(length - decimals, 1)
        return integer_digits + (integer_digits - 1) // 3 + decimals + (1 if decimals else 0)

    return None


def build_data_element_abap_attributes(adt_dataelement):
    """Returns populated ABAP structures with attributes"""

    language = iso_code_to_sap_code(adt_dataelement.master_language)
    definition = adt_dataelement.definition

    if definition.typ not in ('domain', 'predefinedAbapType'):
        raise sap.cli.core.SAPCliError(
            f'Unsupported type of data element {adt_dataelement.name}: {definition.typ}')

    # The values are set in the order of the members to keep the order
    # of XML elements
    dd04v = DD04V()
    dd04v.ROLLNAME = adt_dataelement.name
    dd04v.DDLANGUAGE = language

    if definition.typ == 'domain':
        dd04v.DOMNAME = definition.typ_name

    dd04v.MEMORYID = definition.set_get_parameter or None
    dd04v.LOGFLAG = adt_flag_to_abap(definition.change_document)
    dd04v.HEADLEN = ddic_number(definition.label_heading_length, 2)
    dd04v.SCRLEN1 = ddic_number(definition.label_short_length, 2)
    dd04v.SCRLEN2 = ddic_number(definition.label_medium_length, 2)
    dd04v.SCRLEN3 = ddic_number(definition.label_long_length, 2)
    dd04v.DDTEXT = adt_dataelement.description
    dd04v.REPTEXT = definition.label_heading or None
    dd04v.SCRTEXT_S = definition.label_short or None
    dd04v.SCRTEXT_M = definition.label_medium or None
    dd04v.SCRTEXT_L = definition.label_long or None
    dd04v.DTELMASTER = language
    dd04v.SHLPNAME = definition.search_help or None
    dd04v.SHLPFIELD = definition.search_help_parameter or None
    dd04v.DEFFDNAME = definition.default_component_name or None

    # abapGit does not write the attributes inherited from domains
    if definition.typ == 'domain':
        dd04v.REFKIND = REFKIND_DOMAIN
    else:
        datatype = ADT_TO_DDIC_DATATYPE.get(definition.data_type, definition.data_type)
        dd04v.DATATYPE = datatype
        dd04v.LENG = ddic_number(definition.data_type_length, 6)
        dd04v.DECIMALS = ddic_number(definition.data_type_decimals, 6)
        output_length = ddic_output_length(datatype, definition.data_type_length, definition.data_type_decimals)
        dd04v.OUTPUTLEN = ddic_number(output_length, 6)

    dd04v.LTRFLDDIS = adt_flag_to_abap(definition.left_to_right_direction)
    dd04v.BIDICTRLC = adt_flag_to_abap(definition.deactivate_bidi_filtering)
    dd04v.NOHISTORY = adt_flag_to_abap(definition.deactivate_input_history)

    return (dd04v,)


class DataElementHandler(ObjectHandler):
    """Data element: <name>.dtel.xml"""

    FILE_TYPE = 'dtel'
    METADATA_EXT = 'xml'
    ADT_TYPES = ('DTEL/DE',)

    def checkout(self, connection, adt_type, name, destdir):
        sap.cli.core.printout(name)
        adt_dataelement = sap.adt.DataElement(connection, name)
        adt_dataelement.fetch()

        dump_attributes_to_file(name, build_data_element_abap_attributes(adt_dataelement), '.dtel', 'LCL_OBJECT_DTEL',
                                destdir=destdir)

    def prepare(self, repo_obj):
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

    def checkin(self, context, repo_obj, prepared):
        sap.cli.core.printout('Creating Data Element:', repo_obj.name)

        dd04v = prepared.dd04v

        metadata = sap.adt.ADTCoreData(language='EN', master_language='EN', responsible=context.connection.user.upper(),
                                       description=dd04v.DDTEXT)
        dataelement = sap.adt.DataElement(context.connection, repo_obj.name.upper(), package=context.package_name,
                                          metadata=metadata)

        try:
            dataelement.create(context.corrnr)
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
        definition.deactivate_input_history = abap_flag_to_adt(dd04v.NOHISTORY)
        definition.change_document = abap_flag_to_adt(dd04v.LOGFLAG)
        definition.left_to_right_direction = abap_flag_to_adt(dd04v.LTRFLDDIS)
        definition.deactivate_bidi_filtering = abap_flag_to_adt(dd04v.BIDICTRLC)

        sap.cli.core.printout('Writing Data Element:', repo_obj.name)
        with dataelement.open_editor(corrnr=context.corrnr) as editor:
            editor.push()

        return ObjectCheckinResult([dataelement], [])

    def locate(self, repo_obj, part, line):
        # Data elements have no source code
        return None
