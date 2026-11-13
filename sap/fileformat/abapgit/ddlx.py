"""Metadata extensions in the abapGit serialization"""

import sap.adt
import sap.cli.core
from sap.fileformat import ObjectHandler, ObjectCheckinResult
from sap.fileformat.abapgit.cds import prepare_cds_source, checkin_cds_source
from sap.fileformat.abapgit.files import dump_attributes_to_file, write_source, locate_main_source
from sap.platform.abap.ddic import DDLX, DDLX_METADATA


def build_metadata_extension_abap_attributes(adt_ddlx):
    """Returns populated ABAP structure with attributes"""

    return DDLX(METADATA=DDLX_METADATA(NAME=adt_ddlx.name,
                                       DESCRIPTION=adt_ddlx.description,
                                       MASTER_LANGUAGE=adt_ddlx.master_language))


class MetadataExtensionHandler(ObjectHandler):
    """Metadata Extension: <name>.ddlx.xml and <name>.ddlx.asddlxs"""

    FILE_TYPE = 'ddlx'
    METADATA_EXT = 'xml'
    ADT_TYPES = ('DDLX/EX',)

    def checkout(self, connection, adt_type, name, destdir):
        sap.cli.core.printout(name)
        adt_ddlx = sap.adt.MetadataExtension(connection, name)
        adt_ddlx.fetch()

        write_source(adt_ddlx.text, name, '.ddlx', destdir=destdir, fileext='asddlxs')

        ddlx = build_metadata_extension_abap_attributes(adt_ddlx)
        dump_attributes_to_file(name, (ddlx,), '.ddlx', 'LCL_OBJECT_DDLX', destdir=destdir)

    def prepare(self, repo_obj):
        # Old abapGit versions stored the source code in the XML file but abapGit
        # has been writing it to the file .asddlxs for years
        return prepare_cds_source(repo_obj, DDLX, lambda ddlx: ddlx.METADATA.DESCRIPTION, '.asddlxs',
                                  'Metadata Extension')

    def checkin(self, context, repo_obj, prepared):
        adt_object, source_file = checkin_cds_source(context, repo_obj, prepared, sap.adt.MetadataExtension, 'Metadata Extension')

        return ObjectCheckinResult([adt_object], [source_file])

    def locate(self, repo_obj, part, line):
        return locate_main_source(repo_obj, part, line, '.ddlx.asddlxs')
