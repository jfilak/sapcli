"""Data definitions (CDS views) in the abapGit serialization"""

import re

import sap.adt
import sap.cli.core
from sap.fileformat import ObjectHandler, ObjectCheckinResult
from sap.fileformat.abapgit.cds import prepare_cds_source, checkin_cds_source
from sap.fileformat.abapgit.files import dump_attributes_to_file, write_source, locate_main_source
from sap.platform.abap.ddic import DDLS
from sap.platform.language import iso_code_to_sap_code

# ADT does not provide the source type codes, so they are derived from the
# definition statement - the first matching pattern wins
DDLS_SOURCE_TYPE_PATTERNS = (
    ('P', re.compile(r'\bas\s+projection\s+on\b', re.IGNORECASE)),
    ('W', re.compile(r'\bdefine\s+(root\s+)?view\s+entity\b', re.IGNORECASE)),
    ('V', re.compile(r'\bdefine\s+(root\s+)?view\b', re.IGNORECASE)),
    ('F', re.compile(r'\bdefine\s+table\s+function\b', re.IGNORECASE)),
    ('A', re.compile(r'\bdefine\s+(root\s+)?abstract\s+entity\b', re.IGNORECASE)),
)


def ddls_source_type(source):
    """Returns the abapGit source type of the given data definition source code
       or None if the source type is not known.
    """

    return next((source_type for source_type, pattern in DDLS_SOURCE_TYPE_PATTERNS if pattern.search(source)), None)


def build_data_definition_abap_attributes(adt_ddl, source):
    """Returns populated ABAP structure with attributes"""

    return DDLS(DDLNAME=adt_ddl.name,
                DDLANGUAGE=iso_code_to_sap_code(adt_ddl.master_language),
                DDTEXT=adt_ddl.description,
                SOURCE_TYPE=ddls_source_type(source))


class DataDefinitionHandler(ObjectHandler):
    """Data definition: <name>.ddls.xml, <name>.ddls.asddls and optional
       <name>.ddls.baseinfo
    """

    FILE_TYPE = 'ddls'
    METADATA_EXT = 'xml'
    ADT_TYPES = ('DDLS/DF',)

    def checkout(self, connection, adt_type, name, destdir):
        sap.cli.core.printout(name)
        adt_ddl = sap.adt.DataDefinition(connection, name)
        adt_ddl.fetch()

        source = adt_ddl.text
        # abapGit makes sure the source code ends with a new line
        if not source.endswith('\n'):
            source += '\n'

        write_source(source, name, '.ddls', destdir=destdir, fileext='asddls')

        ddls = build_data_definition_abap_attributes(adt_ddl, source)
        if ddls.SOURCE_TYPE is None:
            sap.cli.core.printerr(f'Unknown source type of data definition {name}')

        dump_attributes_to_file(name, (ddls,), '.ddls', 'LCL_OBJECT_DDLS', destdir=destdir)

    def prepare(self, repo_obj):
        return prepare_cds_source(repo_obj, DDLS, lambda ddls: ddls.DDTEXT, '.asddls', 'Data Definition')

    def checkin(self, context, repo_obj, prepared):
        ddl, source_file = checkin_cds_source(context, repo_obj, prepared, sap.adt.DataDefinition, 'Data Definition')

        used_files = [source_file]

        # The base info lists the objects the data definition uses and ADT
        # computes it from the source code
        baseinfo_file = repo_obj.path[:-4] + '.baseinfo'
        if baseinfo_file in repo_obj.files:
            used_files.append(baseinfo_file)

        return ObjectCheckinResult([ddl], used_files)

    def locate(self, repo_obj, part, line):
        return locate_main_source(repo_obj, part, line, '.ddls.asddls')
