"""Interfaces in the abapGit serialization"""

from types import SimpleNamespace

import sap.adt
import sap.adt.checkin
import sap.adt.errors
import sap.adt.checks
import sap.platform.abap.abapgit
from sap.platform.abap.localrepository import ObjectHandler, ObjectCheckinResult
from sap.platform.abap.abapgit.files import download_abap_source, dump_attributes_to_file, locate_main_source
from sap.platform.abap.ddic import VSEOINTERF, DESCRIPTIONS_SUB
from sap.platform.language import iso_code_to_sap_code


def build_interface_abap_attributes(adt_intf):
    """Returns populated ABAP structure with attributes"""

    vseointerf = VSEOINTERF(CLSNAME=adt_intf.name, DESCRIPT=adt_intf.description)
    vseointerf.VERSION = '1' if adt_intf.active == 'active' else '0'
    vseointerf.LANGU = iso_code_to_sap_code(adt_intf.master_language)
    vseointerf.STATE = '0' if adt_intf.modeled else '1'
    # TODO: do we really need this information?
    vseointerf.EXPOSURE = '2'
    # TODO: adt_intfs:abapClass/abapSource:syntaxConfiguration/abapSource:language/abapSource:version
    #   X = Standard ABAP (Unicode), 2 3 4 -> ABAP PaaS?
    vseointerf.UNICODE = 'X'

    return vseointerf


class InterfaceHandler(ObjectHandler):
    """Interface: <name>.intf.xml and <name>.intf.abap"""

    FILE_TYPE = 'intf'
    METADATA_EXT = 'xml'
    ADT_TYPES = ('INTF/OI',)

    def checkout(self, connection, adt_type, name, destdir, observer):
        observer.checking_out(name)
        intf = sap.adt.Interface(connection, name)
        intf.fetch()

        download_abap_source(observer, name, intf, '.intf', destdir=destdir)

        vseointerf = build_interface_abap_attributes(intf)
        dump_attributes_to_file(observer, name, (vseointerf,), '.intf', 'LCL_OBJECT_INTF', destdir=destdir)

    def prepare(self, repo_obj, observer):
        if not repo_obj.files:
            raise sap.adt.errors.ExceptionCheckinFailure(f'No source file for interface {repo_obj.name}')

        if len(repo_obj.files) > 1:
            raise sap.adt.errors.ExceptionCheckinFailure(
                f'Too many source files for interface {repo_obj.name}: {",".join(repo_obj.files)}')

        source_file = repo_obj.files[0]

        if not source_file.endswith('.abap'):
            raise sap.adt.errors.ExceptionCheckinFailure(f'No .abap suffix of source file for interface {repo_obj.name}')

        with open(repo_obj.path, encoding='utf-8') as abap_data_file:
            # DESCRIPTIONS_SUB is parsed only to detect abapGit XML format changes
            # - ADT generates the sub-component descriptions from source code
            abap_data = sap.platform.abap.abapgit.from_xml(
                [VSEOINTERF, sap.platform.abap.abapgit.OptionalBody(DESCRIPTIONS_SUB)],
                abap_data_file.read())['VSEOINTERF']

        with open(source_file, 'r', encoding='utf-8') as source:
            source_code = source.read()

        return SimpleNamespace(abap_data=abap_data, source_file=source_file, source_code=source_code)

    def checkin(self, context, repo_obj, prepared):
        context.observer.creating('Interface', repo_obj.name)

        metadata = sap.adt.ADTCoreData(language='EN', master_language='EN', responsible=context.connection.user.upper(),
                                       description=prepared.abap_data.DESCRIPT)
        interface = sap.adt.Interface(context.connection, repo_obj.name.upper(), package=context.package_name,
                                      metadata=metadata)

        sap.adt.checkin.create_in_package(interface, context.corrnr, context.package_name, 'interface')

        context.observer.writing('Interface', repo_obj.name)
        sap.adt.checks.write_source(prepared.source_code, interface, corrnr=context.corrnr,
                                    source_label=prepared.source_file,
                                    check_before_save=context.check_before_save)

        return ObjectCheckinResult([interface], [prepared.source_file])

    def locate(self, repo_obj, part, line):
        return locate_main_source(repo_obj, part, line, '.intf.abap')
