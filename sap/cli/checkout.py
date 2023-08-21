"""ADT Object export"""
import enum
import os
import sys

import sap.adt
import sap.cli.core

from sap.platform.abap.ddic import VSEOCLASS, PROGDIR, TPOOL, VSEOINTERF, DEVC, AREAT, INCLUDES, FUNCTIONS, \
    FUNCTION_LINE, IMPORT_TYPE, CHANGING_TYPE, EXPORT_TYPE, TABLE_TYPE, EXCEPTION_TYPE, DOCUMENTATION_TYPE, RSFDO, \
    TPOOL_LINE
from sap.platform.language import iso_code_to_sap_code

from sap.platform.abap.abapgit import DOT_ABAP_GIT, XMLWriter, AbapToAbapGitTranslator


class SourceCodeFormat(enum.Enum):
    """Source code format of ADT objects"""

    ABAP = 'ABAP'
    ABAPGIT = 'ABAPGIT'


class CommandGroup(sap.cli.core.CommandGroup):
    """Commands for exporting ADT objects"""

    def __init__(self):
        super().__init__('checkout')


def build_filename(object_name, typsfx, fileext, destdir=None):
    """Creates file name"""

    filename = f'{object_name}{typsfx}.{fileext}'.lower()

    if destdir is not None:
        filename = os.path.join(destdir, filename)

    return filename


def dump_attributes_to_file(object_name, abap_attributes, typsfx, ag_serializer, destdir=None):
    """Writes ABAP attributes to a file"""

    filename = build_filename(object_name, typsfx, 'xml', destdir=destdir)
    with open(filename, 'w', encoding='utf8') as dest:
        writer = XMLWriter(ag_serializer, dest)

        for attributes in abap_attributes:
            writer.add(attributes)

        writer.close()


def write_source(source, object_name, typsfx, destdir=None):
    """Write source code to file"""

    filename = build_filename(object_name, typsfx, 'abap', destdir=destdir)
    with open(filename, 'w', encoding='utf8') as dest:
        dest.write(source)


def download_abapgit_source(object_name, source_object, typsfx, translate_fn, destdir=None):
    """Saves the source code of object in AbapGit format"""

    try:
        source_code = translate_fn(source_object)
    except sap.adt.errors.ADTError as err:
        sap.cli.core.printerr(f'Download of AbapGit source code failed: {err}')
    else:
        write_source(source_code, object_name, typsfx, destdir)


def download_abap_source(object_name, source_object, typsfx, destdir=None):
    """Reads the text and saves it in the corresponding file"""

    try:
        text = source_object.text
    except sap.adt.errors.ADTError as err:
        sap.cli.core.printerr(f'Download of ABAP source code failed: {err}')
    else:
        write_source(text, object_name, typsfx, destdir)


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


def checkout_class(connection, name, destdir=None):
    """Download entire class"""

    clas = sap.adt.Class(connection, name)
    clas.fetch()

    download_abap_source(name, clas, '.clas', destdir=destdir)
    download_abap_source(name, clas.definitions, '.clas.locals_def', destdir=destdir)
    download_abap_source(name, clas.implementations, '.clas.locals_imp', destdir=destdir)
    download_abap_source(name, clas.test_classes, '.clas.testclasses', destdir=destdir)

    vseoclass = build_class_abap_attributes(clas)
    dump_attributes_to_file(name, (vseoclass,), '.clas', 'LCL_OBJECT_CLAS', destdir=destdir)


@CommandGroup.argument('name')
@CommandGroup.command('class')
def abapclass(connection, args):
    """Download all class sources command wrapper"""

    checkout_class(connection, args.name.upper())


def build_program_abap_attributes(adt_program):
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

    tpool = TPOOL()
    tpool.append(ID='R', ENTRY=adt_program.description, LENGTH=len(adt_program.description))

    return (progdir, tpool)


def checkout_program(connection, name, destdir=None):
    """Download program sources"""

    adt_program = sap.adt.Program(connection, name)
    adt_program.fetch()

    download_abap_source(name, adt_program, '.prog', destdir=destdir)

    progdir, tpool = build_program_abap_attributes(adt_program)
    dump_attributes_to_file(name, (progdir, tpool), '.prog', 'LCL_OBJECT_PROG', destdir=destdir)


@CommandGroup.argument('name')
@CommandGroup.command()
def program(connection, args):
    """Download program sources command wrapper"""

    checkout_program(connection, args.name.upper())


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


def checkout_interface(connection, name, destdir=None):
    """Download interface sources"""

    intf = sap.adt.Interface(connection, name)
    intf.fetch()

    download_abap_source(name, intf, '.intf', destdir=destdir)

    vseointerf = build_interface_abap_attributes(intf)
    dump_attributes_to_file(name, (vseointerf,), '.prog', 'LCL_OBJECT_INTF', destdir=destdir)


@CommandGroup.argument('name')
@CommandGroup.command()
def interface(connection, args):
    """Download interface sources command wrapper"""

    checkout_interface(connection, args.name.upper())


def build_function_module_abap_attributes(func_module):
    """Returns populated FUNCTION_LINE ABAP structure with attributes"""

    func_line = FUNCTION_LINE()
    func_line.FUNCNAME = func_module.name
    func_line.REMOTE_CALL = 'R' if func_module.processing_type == 'rfc' else None
    func_line.SHORT_TEXT = func_module.description

    func_local_interface = func_module.get_local_interface()
    interface_helper = {
        'IMPORTING': (IMPORT_TYPE, 'IMPORT'),
        'CHANGING': (CHANGING_TYPE, 'CHANGING'),
        'EXPORTING': (EXPORT_TYPE, 'EXPORT'),
        'TABLES': (TABLE_TYPE, 'TABLES'),
        'EXCEPTIONS': (EXCEPTION_TYPE, 'EXCEPTION')
    }

    for param_type, params in func_local_interface.items():
        ddic_type, func_line_attr = interface_helper[param_type]
        ddic_type = ddic_type()
        for param in params:
            ddic_type.append(param)

        setattr(func_line, func_line_attr, ddic_type if ddic_type else None)

    documentation = DOCUMENTATION_TYPE()
    for param_type in func_module.DOCUMENTATION_ORDER:
        for param in func_local_interface[param_type]:
            if param_type == 'EXCEPTIONS':
                documentation.append(RSFDO(PARAMETER=param.EXCEPTION, KIND='X'))
            else:
                documentation.append(RSFDO(PARAMETER=param.PARAMETER, KIND='P'))

    func_line.DOCUMENTATION = documentation
    return func_line


def build_function_group_abap_attributes(adt_funcgrp, function_modules, funcgrp_includes):
    """Returns populated ABAP structure with attributes"""

    areat = AREAT(adt_funcgrp.description)
    includes = INCLUDES()
    for include in funcgrp_includes:
        includes.append(f'<SOBJ_NAME>{include.name}</SOBJ_NAME>')

    functions = FUNCTIONS()
    for func_module in function_modules:
        functions.append(build_function_module_abap_attributes(func_module))

    return areat, includes, functions


def build_user_fn_include_abap_attributes(include, funcgrp):
    """Returns populated PROGDIR ABAP structure with attributes for user-defined function include"""

    progdir = PROGDIR()
    progdir.NAME = include.name
    progdir.SUBC = 'I'
    progdir.APPL = 'S'
    progdir.RLOAD = 'E' if include.description else None
    progdir.UCCHECK = 'X' if funcgrp.active_unicode_check else None

    tpool = TPOOL()
    if include.description:
        tpool_line = TPOOL_LINE()
        tpool_line.ID = 'R'
        tpool_line.ENTRY = include.description
        tpool_line.LENGTH = len(include.description)
        tpool.append(tpool_line)

    return progdir, tpool


def build_system_fn_include_abap_attributes(include, funcgrp):
    """Returns populated PROGDIR ABAP structure with attributes for system function include"""

    progdir, _ = build_user_fn_include_abap_attributes(include, funcgrp)
    progdir.DBAPL = 'S'
    progdir.DBNA = 'D$'
    progdir.FIXPT = 'X' if funcgrp.fix_point_arithmetic else None
    progdir.LDBNAME = 'D$S'

    return (progdir,)


def checkout_function_include(include_name, funcgrp, destdir=None):
    """Checkout Function Group Include"""

    include = sap.adt.FunctionInclude(funcgrp.connection, include_name, funcgrp.name)
    if include_name.endswith('TOP'):
        include_attrs = build_system_fn_include_abap_attributes(include, funcgrp)
    else:
        include_attrs = build_user_fn_include_abap_attributes(include, funcgrp)

    dump_attributes_to_file(funcgrp.name, include_attrs, f'.fugr.{include.name}', '', destdir=destdir)

    return include


def checkout_function_group(connection, name, destdir=None, source_format=SourceCodeFormat.ABAPGIT):
    """Download function group sources"""

    funcgrp = sap.adt.FunctionGroup(connection, name)
    function_modules = []
    includes = []

    walk_step = funcgrp.walk()[0]  # Function group always has only a single step
    objects = walk_step[2]
    for obj in objects:
        if obj.name.endswith('UXX'):
            sap.cli.core.printout(f'Skipping system generated "UXX" function group include: {obj.name}.')
            continue

        if obj.typ == 'FUGR/FF':
            adt_obj = sap.adt.FunctionModule(funcgrp.connection, obj.name, funcgrp.name)
            function_modules.append(adt_obj)
            if source_format == SourceCodeFormat.ABAPGIT:
                download_abapgit_source(funcgrp.name, adt_obj, f'.fugr.{adt_obj.name}',
                                        AbapToAbapGitTranslator.translate_function_module, destdir=destdir)
            else:
                download_abap_source(funcgrp.name, adt_obj, f'.fugr.{adt_obj.name}', destdir=destdir)

        elif obj.typ in ('FUGR/I', 'FUGR/PX'):
            adt_obj = checkout_function_include(obj.name, funcgrp, destdir=destdir)
            includes.append(adt_obj)
            download_abap_source(funcgrp.name, adt_obj, f'.fugr.{adt_obj.name}', destdir=destdir)
        else:
            raise sap.cli.core.SAPCliError(f'Unsupported function group object: {obj.typ} {obj.name}')

    funcgrp_attrs = build_function_group_abap_attributes(funcgrp, function_modules, includes)
    dump_attributes_to_file(funcgrp.name, funcgrp_attrs, '.fugr', 'LCL_OBJECT_FUGR', destdir=destdir)


@CommandGroup.argument('-f', '--format', type=str,
                       choices=[SourceCodeFormat.ABAP.value, SourceCodeFormat.ABAPGIT.value],
                       default=SourceCodeFormat.ABAPGIT.value)
@CommandGroup.argument('name')
@CommandGroup.command()
def function_group(connection, args):
    """Download function group sources command wrapper"""

    try:
        checkout_function_group(connection, args.name.upper(), source_format=SourceCodeFormat(args.format))
    except sap.cli.core.SAPCliError as ex:
        sap.cli.core.printerr(f'Checkout failed: {str(ex)}')
        return 1

    return 0


def checkout_objects(connection, objects, destdir=None):
    """Checkout all objects from the give list"""

    # This could be a global variable but it breaks mock patching in tests
    checkouters = {
        'PROG/P': checkout_program,
        'CLAS/OC': checkout_class,
        'INTF/OI': checkout_interface,
        'FUGR/F': checkout_function_group,
    }

    if not os.path.isdir(destdir):
        os.makedirs(destdir)

    for obj in objects:
        try:
            checkouters[obj.typ](connection, obj.name, destdir)
        except KeyError:
            print(f'Unsupported object: {obj.typ} {obj.name}', file=sys.stderr)


def make_repo_dir_for_package(args):
    """Creates and populates the directory to checkout the package into."""

    repo_dir = args.directory
    if not repo_dir:
        repo_dir = args.name

    repo_dir = os.path.abspath(repo_dir)

    if not os.path.isdir(repo_dir):
        os.makedirs(repo_dir)

    dot_abapgit = DOT_ABAP_GIT.for_new_repo(STARTING_FOLDER='/' + args.starting_folder + '/')

    repo_file = os.path.join(repo_dir, '.abapgit.xml')
    with open(repo_file, 'w', encoding='utf8') as dest:
        sap.platform.abap.to_xml(dot_abapgit, dest=dest, top_element='DATA')

    return repo_dir


def build_package_abap_attributes(adt_package):
    """Returns populated ABAP structure with attributes"""

    return DEVC(CTEXT=adt_package.description)


def checkout_package(connection, name, destdir=None):
    """Creates ABAP Package files"""

    adt_package = sap.adt.Package(connection, name)
    adt_package.fetch()

    devc = build_package_abap_attributes(adt_package)
    dump_attributes_to_file('package', (devc,), '.devc', 'LCL_OBJECT_DEVC', destdir=destdir)


# @CommandGroup.argument('--folder-logic', choices=['full', 'prefix'], default='prefix')
@CommandGroup.argument('--recursive', action='store_true', default=False)
@CommandGroup.argument('--starting-folder', default='src')
@CommandGroup.argument('directory', nargs='?', default=None,
                       help='To checkout the package into it; default=<PACKAGE NAME>')
@CommandGroup.argument('name')
@CommandGroup.command()
def package(connection, args):
    """Download sources of objects from the given ABAP package"""

    repo_dir = make_repo_dir_for_package(args)
    source_code_dir = os.path.join(repo_dir, args.starting_folder)

    explored = sap.adt.Package(connection, args.name)

    for package_name_hier, _, objects in sap.adt.package.walk(explored):
        destdir = os.path.abspath(source_code_dir)

        if len(package_name_hier) == 1:
            destdir = os.path.join(destdir, package_name_hier[0].lower())
        elif len(package_name_hier) > 1:
            hier_path = os.path.join(*package_name_hier)
            destdir = os.path.join(destdir, hier_path.lower())

        if not package_name_hier:
            package_name = args.name
        else:
            package_name = package_name_hier[-1]

        checkout_objects(connection, objects, destdir=destdir)
        checkout_package(connection, package_name.upper(), destdir=destdir)

        if not args.recursive:
            break
