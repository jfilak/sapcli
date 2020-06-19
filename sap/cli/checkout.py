"""ADT Object export"""

import os
import sys

import sap.adt
import sap.cli.core

from sap.platform.abap.ddic import VSEOCLASS, PROGDIR, TPOOL, VSEOINTERF, DEVC
from sap.platform.language import iso_code_to_sap_code

from sap.platform.abap.abapgit import DOT_ABAP_GIT, XMLWriter


class CommandGroup(sap.cli.core.CommandGroup):
    """Commands for exporting ADT objects"""

    def __init__(self):
        super(CommandGroup, self).__init__('checkout')


def build_filename(object_name, typsfx, fileext, destdir=None):
    """Creates file name"""

    filename = f'{object_name}{typsfx}.{fileext}'.lower()

    if destdir is not None:
        filename = os.path.join(destdir, filename)

    return filename


def dump_attributes_to_file(object_name, abap_attributes, typsfx, ag_serializer, destdir=None):
    """Writes ABAP attributes to a file"""

    filename = build_filename(object_name, typsfx, 'xml', destdir=destdir)
    with open(filename, 'w') as dest:
        writer = XMLWriter(ag_serializer, dest)

        for attributes in abap_attributes:
            writer.add(attributes)

        writer.close()


def download_abap_source(object_name, source_object, typsfx, destdir=None):
    """Reads the text and saves it in the corresponding file"""

    try:
        text = source_object.text
    except sap.adt.errors.ADTError as err:
        print(err, file=sys.stderr)
    else:
        filename = build_filename(object_name, typsfx, 'abap', destdir=destdir)
        with open(filename, 'w') as dest:
            dest.write(text)


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


def checkout_objects(connection, objects, destdir=None):
    """Checkout all objects from the give list"""

    # This could be a global variable but it breaks mock patching in tests
    checkouters = {
        'PROG/P': checkout_program,
        'CLAS/OC': checkout_class,
        'INTF/OI': checkout_interface,
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
    with open(repo_file, 'w') as dest:
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
