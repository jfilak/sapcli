"""Access controls (CDS roles) in the abapGit serialization"""

import sap.adt
from sap.platform.abap.localrepository import ObjectHandler, ObjectCheckinResult
from sap.platform.abap.abapgit.cds import prepare_cds_source, checkin_cds_source
from sap.platform.abap.abapgit.files import dump_attributes_to_file, write_source, locate_main_source
from sap.platform.abap.ddic import DCLS
from sap.platform.language import iso_code_to_sap_code


def build_access_control_abap_attributes(adt_dcl):
    """Returns populated ABAP structure with attributes"""

    return DCLS(DCLNAME=adt_dcl.name,
                DCLLANGUAGE=iso_code_to_sap_code(adt_dcl.master_language),
                DDTEXT=adt_dcl.description)


class AccessControlHandler(ObjectHandler):
    """Access Control: <name>.dcls.xml and <name>.dcls.asdcls"""

    FILE_TYPE = 'dcls'
    METADATA_EXT = 'xml'
    ADT_TYPES = ('DCLS/DL',)

    def checkout(self, connection, adt_type, name, destdir, observer):
        observer.checking_out(name)
        adt_dcl = sap.adt.AccessControl(connection, name)
        adt_dcl.fetch()

        write_source(observer, adt_dcl.text, name, '.dcls', destdir=destdir, fileext='asdcls')

        dcls = build_access_control_abap_attributes(adt_dcl)
        dump_attributes_to_file(observer, name, (dcls,), '.dcls', 'LCL_OBJECT_DCLS', destdir=destdir)

    def prepare(self, repo_obj, observer):
        return prepare_cds_source(repo_obj, DCLS, lambda dcls: dcls.DDTEXT, '.asdcls', 'Access Control')

    def checkin(self, context, repo_obj, prepared):
        adt_object, source_file = checkin_cds_source(context, repo_obj, prepared, sap.adt.AccessControl, 'Access Control')

        return ObjectCheckinResult([adt_object], [source_file])

    def locate(self, repo_obj, part, line):
        return locate_main_source(repo_obj, part, line, '.dcls.asdcls')
