"""Domains in the abapGit serialization"""

from types import SimpleNamespace

from sap import get_logger

import sap.adt
import sap.adt.domain
import sap.adt.errors
import sap.errors
import sap.platform.abap.abapgit
from sap.platform.abap.localrepository import ObjectHandler, ObjectCheckinResult
from sap.platform.abap.abapgit.ddic import ADT_TO_DDIC_DATATYPE, ddic_number, adt_flag_to_abap, abap_flag_to_adt
from sap.platform.abap.abapgit.files import dump_attributes_to_file
from sap.platform.abap.ddic import DD01V, DD07V, DD07V_TAB, DD01L_EXTRA
from sap.platform.language import iso_code_to_sap_code


def mod_log():
    """Module logger"""

    return get_logger()


def build_domain_abap_attributes(adt_domain):
    """Returns populated ABAP structures with attributes"""

    language = iso_code_to_sap_code(adt_domain.master_language)
    type_information = adt_domain.content.type_information
    output_information = adt_domain.content.output_information
    value_information = adt_domain.content.value_information

    # The values are set in the order of the members to keep the order
    # of XML elements
    dd01v = DD01V()
    dd01v.DOMNAME = adt_domain.name
    dd01v.DDLANGUAGE = language
    dd01v.DATATYPE = ADT_TO_DDIC_DATATYPE.get(type_information.datatype, type_information.datatype)
    dd01v.LENG = ddic_number(type_information.length, 6)
    dd01v.OUTPUTLEN = ddic_number(output_information.length, 6)
    dd01v.DECIMALS = ddic_number(type_information.decimals, 6)
    dd01v.LOWERCASE = adt_flag_to_abap(output_information.lowercase)
    dd01v.SIGNFLAG = adt_flag_to_abap(output_information.sign_exists)
    dd01v.VALEXI = 'X' if value_information.fix_values else None
    dd01v.ENTITYTAB = value_information.value_table_ref.name or None
    dd01v.CONVEXIT = output_information.conversion_exit or None
    dd01v.DDTEXT = adt_domain.description
    dd01v.OUTPUTSTYLE = ddic_number(output_information.style, 2)
    dd01v.AMPMFORMAT = adt_flag_to_abap(output_information.ampm_format)

    if not value_information.fix_values:
        return (dd01v,)

    dd07v = DD07V_TAB()
    for fix_value in value_information.fix_values:
        dd07v.append(DD07V(VALPOS=fix_value.position, DDLANGUAGE=language, DOMVALUE_L=fix_value.low or None,
                           DOMVALUE_H=fix_value.high or None, DDTEXT=fix_value.text or None))

    return (dd01v, dd07v)


class DomainHandler(ObjectHandler):
    """Domain: <name>.doma.xml"""

    FILE_TYPE = 'doma'
    METADATA_EXT = 'xml'
    ADT_TYPES = ('DOMA/DD',)

    def checkout(self, connection, adt_type, name, destdir, observer):
        observer.checking_out(name)
        adt_domain = sap.adt.Domain(connection, name)
        adt_domain.fetch()

        dump_attributes_to_file(observer, name, build_domain_abap_attributes(adt_domain), '.doma', 'LCL_OBJECT_DOMA',
                                destdir=destdir)

    def prepare(self, repo_obj, observer):
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

    # pylint: disable=too-many-locals
    def checkin(self, context, repo_obj, prepared):
        context.observer.creating('Domain', repo_obj.name)

        dd01v = prepared.dd01v

        metadata = sap.adt.ADTCoreData(language='EN', master_language='EN', responsible=context.connection.user.upper(),
                                       description=dd01v.DDTEXT)
        domain = sap.adt.Domain(context.connection, repo_obj.name.upper(), package=context.package_name, metadata=metadata)

        try:
            domain.create(context.corrnr)
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
        output_information.sign_exists = abap_flag_to_adt(dd01v.SIGNFLAG)
        output_information.lowercase = abap_flag_to_adt(dd01v.LOWERCASE)
        output_information.ampm_format = abap_flag_to_adt(dd01v.AMPMFORMAT)

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

        context.observer.writing('Domain', repo_obj.name)
        with domain.open_editor(corrnr=context.corrnr) as editor:
            editor.push()

        return ObjectCheckinResult([domain], [])

    def locate(self, repo_obj, part, line):
        # Domains have no source code
        return None
