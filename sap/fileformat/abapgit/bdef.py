"""Behavior definitions in the abapGit serialization"""

import sap.adt
import sap.cli.core
from sap.fileformat import ObjectHandler, ObjectCheckinResult
from sap.fileformat.abapgit.cds import prepare_cds_source, checkin_cds_source
from sap.fileformat.abapgit.files import dump_attributes_to_file, write_source, locate_main_source
from sap.platform.abap.ddic import BDEF_LINKS, BDEF, BDEF_LINK


# ABAP language versions of source code based objects
ADT_TO_ABAP_LANGU_VERSION = {
    'standard': 'X',
    'keyUser': '2',
    'cloudDevelopment': '5',
}


def build_behavior_definition_abap_attributes(adt_bdef):
    """Returns populated ABAP structure with attributes"""

    links = BDEF_LINKS([BDEF_LINK(HREF=link.href, REL=link.rel, TYPE=link.typ, TITLE=link.title)
                        for link in adt_bdef.links])

    return BDEF(NAME=adt_bdef.name,
                TYPE=adt_bdef.objtype.code,
                DESCRIPTION=adt_bdef.description,
                DESCRIPTION_TEXT_LIMIT=adt_bdef.description_text_limit,
                LANGUAGE=adt_bdef.language,
                LINKS=links or None,
                MASTER_LANGUAGE=adt_bdef.master_language,
                ABAP_LANGU_VERSION=ADT_TO_ABAP_LANGU_VERSION.get(adt_bdef.abap_language_version),
                SOURCE_URI=adt_bdef.source_uri,
                # The type of the workbench object source code which ADT does not provide
                SOURCE_TYPE='ABAP_SOURCE',
                SOURCE_FIXED_POINT_ARITHMETIC=adt_bdef.fix_point_arithmetic,
                SOURCE_UNICODE_CHECKS_ACTIVE=adt_bdef.active_unicode_check)


class BehaviorDefinitionHandler(ObjectHandler):
    """Behavior Definition: <name>.bdef.xml and <name>.bdef.asbdef"""

    FILE_TYPE = 'bdef'
    METADATA_EXT = 'xml'
    ADT_TYPES = ('BDEF/BDO',)

    def checkout(self, connection, adt_type, name, destdir):
        sap.cli.core.printout(name)
        adt_bdef = sap.adt.BehaviorDefinition(connection, name)
        adt_bdef.fetch()

        write_source(adt_bdef.text, name, '.bdef', destdir=destdir, fileext='asbdef')

        bdef = build_behavior_definition_abap_attributes(adt_bdef)
        dump_attributes_to_file(name, (bdef,), '.bdef', 'LCL_OBJECT_BDEF', destdir=destdir)

    def prepare(self, repo_obj):
        return prepare_cds_source(repo_obj, BDEF, lambda bdef: bdef.DESCRIPTION, '.asbdef', 'Behavior Definition')

    def checkin(self, context, repo_obj, prepared):
        adt_object, source_file = checkin_cds_source(context, repo_obj, prepared, sap.adt.BehaviorDefinition, 'Behavior Definition')

        return ObjectCheckinResult([adt_object], [source_file])

    def locate(self, repo_obj, part, line):
        return locate_main_source(repo_obj, part, line, '.bdef.asbdef')
