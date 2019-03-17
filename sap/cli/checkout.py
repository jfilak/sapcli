"""ADT Object export"""

import os
import sys

import sap.adt
import sap.cli.core

from sap.platform.abap import Structure, StringTable


FOLDER_LOGIC_FULL = 'FULL'
FOLDER_LOGIC_PREFIX = 'PREFIX'


# pylint: disable=invalid-name
class DOT_ABAP_GIT(Structure):
    """ABAP GIT ABAP structure"""

    # pylint: disable=invalid-name
    MASTER_LANGUAGE: str
    # pylint: disable=invalid-name
    STARTING_FOLDER: str
    # pylint: disable=invalid-name
    FOLDER_LOGIC: str
    # pylint: disable=invalid-name
    IGNORE: StringTable

    @staticmethod
    def for_new_repo(MASTER_LANGUAGE: str = 'E', STARTING_FOLDER: str = 'src', FOLDER_LOGIC: str = FOLDER_LOGIC_FULL):
        """Creates new instance of DOT_ABAP_GIT for new repository"""

        IGNORE = ['/.gitignore', '/LICENSE', '/README.md', '/package.json', '/.travis.yml']

        return DOT_ABAP_GIT(MASTER_LANGUAGE=MASTER_LANGUAGE, STARTING_FOLDER=STARTING_FOLDER,
                            FOLDER_LOGIC=FOLDER_LOGIC, IGNORE=IGNORE)


class CommandGroup(sap.cli.core.CommandGroup):
    """Commands for exporting ADT objects"""

    def __init__(self):
        super(CommandGroup, self).__init__('checkout')


def download_abap_source(object_name, source_object, typsfx, destdir=None):
    """Reads the text and saves it in the corresponding file"""

    filename = f'{object_name}{typsfx}.abap'.lower()

    if destdir is not None:
        filename = os.path.join(destdir, filename)

    with open(filename, 'w') as dest:
        dest.write(source_object.text)


def checkout_class(connection, name, destdir=None):
    """Download entire class"""

    clas = sap.adt.Class(connection, name)

    download_abap_source(name, clas, '.clas', destdir=destdir)
    download_abap_source(name, clas.definitions, '.clas.locals_def', destdir=destdir)
    download_abap_source(name, clas.implementations, '.clas.locals_imp', destdir=destdir)
    download_abap_source(name, clas.test_classes, '.clas.testclasses', destdir=destdir)


@CommandGroup.command('class')
@CommandGroup.argument('name')
def abapclass(connection, args):
    """Download all class sources command wrapper"""

    checkout_class(connection, args.name)


def checkout_program(connection, name, destdir=None):
    """Download program sources"""

    download_abap_source(name, sap.adt.Program(connection, name), '.prog', destdir=destdir)


@CommandGroup.command()
@CommandGroup.argument('name')
def program(connection, args):
    """Download program sources command wrapper"""

    checkout_program(connection, args.name)


def checkout_interface(connection, name, destdir=None):
    """Download interface sources"""

    download_abap_source(name, sap.adt.Interface(connection, name), '.intf', destdir=destdir)


@CommandGroup.command()
@CommandGroup.argument('name')
def interface(connection, args):
    """Download interface sources command wrapper"""

    checkout_interface(connection, args.name)


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


@CommandGroup.command()
# @CommandGroup.argument('--folder-logic', choices=['full', 'prefix'], default='prefix')
@CommandGroup.argument('--recursive', action='store_true', default=False)
@CommandGroup.argument('--starting-folder', default='src')
@CommandGroup.argument('directory', nargs='?', default=None,
                       help='To checkout the package into it; default=<PACKAGE NAME>')
@CommandGroup.argument('name')
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

        checkout_objects(connection, objects, destdir=destdir)

        if not args.recursive:
            break
