"""Classes in the abapGit serialization"""

from types import SimpleNamespace

import sap.adt
import sap.adt.errors
import sap.adt.textelements
import sap.adt.checks
import sap.adt.checkin
import sap.platform.abap.abapgit
from sap.platform.abap.localrepository import ObjectHandler, ObjectCheckinResult
from sap.platform.abap.abapgit.files import download_abap_source, dump_attributes_to_file, find_object_file
from sap.platform.abap.abapgit.textpool import (
    build_text_pool,
    download_text_symbols,
    text_symbols_from_tpool,
    write_text_symbols,
)
from sap.platform.abap.ddic import VSEOCLASS, TPOOL, DESCRIPTIONS_SUB
from sap.platform.language import iso_code_to_sap_code


# Class parts by the suffix of their source files
CLASS_PARTS = ('clas', 'locals_def', 'locals_imp', 'testclasses')

# ADT include types of the optional class parts
INCLUDE_TYPES = {
    'locals_def': 'definitions',
    'locals_imp': 'implementations',
    'testclasses': 'testclasses',
}

# Ends of file names of class parts by ADT source parts
SOURCE_PART_FILES = {
    'source/main': '.clas.abap',
    'includes/definitions': '.clas.locals_def.abap',
    'includes/implementations': '.clas.locals_imp.abap',
    'includes/testclasses': '.clas.testclasses.abap',
}


def build_class_abap_attributes(clas):
    """Returns populated ABAP structure with attributes"""

    vseoclass = VSEOCLASS()
    vseoclass.CLSNAME = clas.name
    vseoclass.VERSION = '1' if clas.active == 'active' else '0'
    vseoclass.LANGU = iso_code_to_sap_code(clas.master_language)
    vseoclass.DESCRIPT = clas.description
    vseoclass.STATE = '0' if clas.modeled else '1'
    # TODO: real value!
    vseoclass.CLSCCINCL = 'X'
    vseoclass.FIXPT = 'X' if clas.fix_point_arithmetic else ' '
    # TODO: class:abapClass/abapSource:syntaxConfiguration/abapSource:language/abapSource:version
    #   X = Standard ABAP (Unicode), 2 3 4 -> ABAP PaaS?
    vseoclass.UNICODE = 'X'

    return vseoclass


class ClassHandler(ObjectHandler):
    """Class: <name>.clas.xml, <name>.clas.abap and optional
       <name>.clas.locals_def.abap, <name>.clas.locals_imp.abap,
       <name>.clas.testclasses.abap
    """

    FILE_TYPE = 'clas'
    METADATA_EXT = 'xml'
    ADT_TYPES = ('CLAS/OC',)

    def checkout(self, connection, adt_type, name, destdir, observer):
        observer.checking_out(name)
        clas = sap.adt.Class(connection, name)
        clas.fetch()

        download_abap_source(observer, name, clas, '.clas', destdir=destdir)
        download_abap_source(observer, name, clas.definitions, '.clas.locals_def', destdir=destdir)
        download_abap_source(observer, name, clas.implementations, '.clas.locals_imp', destdir=destdir)
        download_abap_source(observer, name, clas.test_classes, '.clas.testclasses', destdir=destdir)

        abap_attributes = (build_class_abap_attributes(clas),)

        text_symbols = download_text_symbols(observer, sap.adt.textelements.ClassTextElements(connection, name))
        if text_symbols:
            abap_attributes += (build_text_pool(text_symbols),)

        dump_attributes_to_file(observer, name, abap_attributes, '.clas', 'LCL_OBJECT_CLAS', destdir=destdir)

    def prepare(self, repo_obj, observer):
        if find_object_file(repo_obj, '.clas.abap') is None:
            raise sap.adt.errors.ExceptionCheckinFailure(f'No source file for class {repo_obj.name}')

        with open(repo_obj.path, encoding='utf-8') as abap_data_file:
            # DESCRIPTIONS_SUB is parsed only to detect abapGit XML format changes
            # - ADT generates the sub-component descriptions from source code
            results = sap.platform.abap.abapgit.from_xml(
                [VSEOCLASS, sap.platform.abap.abapgit.OptionalBody(TPOOL),
                 sap.platform.abap.abapgit.OptionalBody(DESCRIPTIONS_SUB)],
                abap_data_file.read())

        text_symbols = text_symbols_from_tpool(observer, results.get('TPOOL', []), repo_obj.name)

        parts = []
        for source_file in repo_obj.files:
            if not source_file.endswith('.abap'):
                raise sap.adt.errors.ExceptionCheckinFailure(
                    f'No .abap suffix of source file for class {repo_obj.name}: {source_file}')

            sub_obj_id = source_file.split('.')[-2]
            if sub_obj_id not in CLASS_PARTS:
                observer.warning(f'Unknown class part {source_file}')
                continue

            with open(source_file, 'r', encoding='utf-8') as source:
                parts.append((sub_obj_id, source_file, source.read()))

        return SimpleNamespace(abap_data=results['VSEOCLASS'], text_symbols=text_symbols, parts=parts)

    def checkin(self, context, repo_obj, prepared):
        context.observer.creating('Class', repo_obj.name)

        metadata = sap.adt.ADTCoreData(language='EN', master_language='EN', responsible=context.connection.user.upper(),
                                       description=prepared.abap_data.DESCRIPT)
        clas = sap.adt.Class(context.connection, repo_obj.name.upper(), package=context.package_name, metadata=metadata)

        created = sap.adt.checkin.create_in_package(clas, context.corrnr, context.package_name, 'class')

        description = prepared.abap_data.DESCRIPT or ''
        if not created and (clas.description or '') != description:
            context.observer.writing('Clas', repo_obj.name, 'description')
            clas.write_description(description, corrnr=context.corrnr)

        class_parts = {
            'clas': clas,
            'locals_def': clas.definitions,
            'locals_imp': clas.implementations,
            'testclasses': clas.test_classes,
        }

        used_files = []

        for sub_obj_id, source_file, source_code in prepared.parts:
            context.observer.writing('Clas', repo_obj.name, sub_obj_id)

            sap.adt.checks.write_source(source_code, class_parts[sub_obj_id], corrnr=context.corrnr,
                                        source_label=source_file,
                                        check_before_save=context.check_before_save)

            used_files.append(source_file)

        if not created:
            # The repository is the truth: the includes of the existing class
            # which have no file are emptied - instead of deleting the class
            self._empty_includes_without_file(context, repo_obj, prepared, clas, class_parts)

        abap_objects = [clas]

        if prepared.text_symbols:
            context.observer.writing('Clas', repo_obj.name, 'text elements')
            text_elements = sap.adt.textelements.ClassTextElements(context.connection, repo_obj.name.upper())
            write_text_symbols(text_elements, prepared.text_symbols, context.corrnr)
            abap_objects.append(text_elements)

        return ObjectCheckinResult(abap_objects, used_files)

    def _empty_includes_without_file(self, context, repo_obj, prepared, clas, class_parts):
        """Writes empty source code to the includes of the existing class
           which have no file in the repository. Includes which do not exist
           in the system are not created.
        """

        parts_with_file = [sub_obj_id for sub_obj_id, _, _ in prepared.parts]

        for sub_obj_id, include_type in INCLUDE_TYPES.items():
            if sub_obj_id in parts_with_file or include_type not in clas.include_types:
                continue

            context.observer.writing('Clas', repo_obj.name, f'{sub_obj_id} (empty)')
            sap.adt.checks.write_source('', class_parts[sub_obj_id], corrnr=context.corrnr,
                                        check_before_save=context.check_before_save)

    def locate(self, repo_obj, part, line):
        file_name_end = SOURCE_PART_FILES.get(part)
        if file_name_end is None:
            return None

        file_path = find_object_file(repo_obj, file_name_end)
        if file_path is None:
            return None

        return (file_path, line)
