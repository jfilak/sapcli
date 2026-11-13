"""Programs and includes in the abapGit serialization"""

from types import SimpleNamespace

from sap import get_logger

import sap.adt
import sap.adt.errors
import sap.adt.textelements
import sap.cli.core
import sap.fileformat.adt
import sap.platform.abap.abapgit
from sap.fileformat import ObjectHandler, ObjectCheckinResult
from sap.fileformat.abapgit.files import download_abap_source, dump_attributes_to_file, locate_main_source
from sap.fileformat.abapgit.textpool import (
    build_text_pool,
    download_text_symbols,
    text_symbols_from_tpool,
    write_text_symbols,
)
from sap.platform.abap.ddic import PROGDIR, CUA, TPOOL, SUBC_EXECUTABLE_PROGRAM, SUBC_INCLUDE


def mod_log():
    """Module logger"""

    return get_logger()


def build_program_abap_attributes(adt_program, text_symbols=()):
    """Returns populated ABAP structure with attributes"""

    progdir = PROGDIR()
    progdir.NAME = adt_program.name
    progdir.STATE = 'A' if adt_program.active == 'active' else 'S'
    progdir.FIXPT = 'X' if adt_program.fix_point_arithmetic else ' '
    progdir.DBAPL = adt_program.application_database
    progdir.VARCL = 'X' if adt_program.case_sensitive else ' '
    progdir.SUBC = adt_program.program_type
    progdir.LDBNAME = adt_program.logical_database.reference.name
    progdir.UCCHECK = 'X'

    # text symbols (I) precede the title (R) to keep the entries ordered by ID
    tpool = build_text_pool(text_symbols)
    tpool.append(ID='R', ENTRY=adt_program.description, LENGTH=len(adt_program.description))

    return (progdir, tpool)


class ProgramHandler(ObjectHandler):
    """Program or include: <name>.prog.xml and <name>.prog.abap

       Includes can be checked in but they are not checked out.
    """

    FILE_TYPE = 'prog'
    METADATA_EXT = 'xml'
    ADT_TYPES = ('PROG/P',)

    def checkout(self, connection, adt_type, name, destdir):
        sap.cli.core.printout(name)
        adt_program = sap.adt.Program(connection, name)
        adt_program.fetch()

        download_abap_source(name, adt_program, '.prog', destdir=destdir)

        text_symbols = download_text_symbols(sap.adt.textelements.ProgramTextElements(connection, name))
        progdir, tpool = build_program_abap_attributes(adt_program, text_symbols=text_symbols)
        dump_attributes_to_file(name, (progdir, tpool), '.prog', 'LCL_OBJECT_PROG', destdir=destdir)

    def prepare(self, repo_obj):
        if not repo_obj.files:
            raise sap.adt.errors.ExceptionCheckinFailure(f'No source file for program {repo_obj.name}')

        if len(repo_obj.files) > 1:
            raise sap.adt.errors.ExceptionCheckinFailure(
                f'Too many source files for program {repo_obj.name}: {",".join(repo_obj.files)}')

        source_file = repo_obj.files[0]

        if not source_file.endswith('.abap'):
            raise sap.adt.errors.ExceptionCheckinFailure(f'No .abap suffix of source file for program {repo_obj.name}')

        with open(repo_obj.path, encoding='utf-8') as abap_data_file:
            results = sap.platform.abap.abapgit.from_xml(
                [PROGDIR, sap.platform.abap.abapgit.OptionalBody(CUA), TPOOL], abap_data_file.read())

        progdir = results['PROGDIR']
        # TODO: how to handle CUA?
        tpool = results['TPOOL']

        if progdir.SUBC not in (SUBC_EXECUTABLE_PROGRAM, SUBC_INCLUDE):
            raise sap.adt.errors.ExceptionCheckinFailure(f'Unknown program type {progdir.SUBC}')

        description = None
        for text in tpool:
            if text.ID == 'R':
                description = text.ENTRY

        # ADT does not allow editing text elements of includes
        supported_ids = ('I',) if progdir.SUBC == SUBC_EXECUTABLE_PROGRAM else ()
        text_symbols = text_symbols_from_tpool(tpool, repo_obj.name, known_ids=('R',), supported_ids=supported_ids)

        with open(source_file, 'r', encoding='utf-8') as source:
            source_code = source.read()

        return SimpleNamespace(progdir=progdir, description=description, text_symbols=text_symbols,
                               source_file=source_file, source_code=source_code)

    def checkin(self, context, repo_obj, prepared):
        sap.cli.core.printout('Creating Program:', repo_obj.name)

        metadata = sap.adt.ADTCoreData(language='EN', master_language='EN', responsible=context.connection.user.upper())
        if prepared.progdir.SUBC == SUBC_EXECUTABLE_PROGRAM:
            program = sap.adt.Program(context.connection, repo_obj.name, package=context.package_name, metadata=metadata)
        else:
            sap.cli.core.printout('Creating Include:', repo_obj.name)
            program = sap.adt.Include(context.connection, repo_obj.name, package=context.package_name, metadata=metadata)

        if prepared.description is not None:
            program.description = prepared.description

        try:
            program.create(context.corrnr)
        except sap.adt.errors.ExceptionResourceCreationFailure as err:
            if not str(err).endswith(f'A program or include already exists with the name {repo_obj.name.upper()}'):
                raise

            mod_log().info(err.message)

        sap.cli.core.printout('Writing Program:', repo_obj.name)
        sap.fileformat.adt.write_source(prepared.source_code, program, corrnr=context.corrnr,
                                        source_label=prepared.source_file,
                                        check_before_save=context.check_before_save)

        abap_objects = [program]

        if prepared.text_symbols:
            sap.cli.core.printout('Writing Program:', repo_obj.name, 'text elements')
            text_elements = sap.adt.textelements.ProgramTextElements(context.connection, repo_obj.name.upper())
            write_text_symbols(text_elements, prepared.text_symbols, context.corrnr)
            # ADT does not activate inactive text elements together with the program
            abap_objects.append(text_elements)

        return ObjectCheckinResult(abap_objects, [prepared.source_file])

    def locate(self, repo_obj, part, line):
        return locate_main_source(repo_obj, part, line, '.prog.abap')
