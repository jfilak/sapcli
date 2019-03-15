"""ADT Object export"""

import os
import sys

import sap.adt
import sap.cli.core


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

    repo_file = os.path.join(repo_dir, '.abapgit.xml')
    with open(repo_file, 'w') as dest:
        dest.write(f'''<?xml version="1.0" encoding="utf-8"?>
<asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
 <asx:values>
  <DATA>
   <MASTER_LANGUAGE>E</MASTER_LANGUAGE>
   <STARTING_FOLDER>/{args.starting_folder}/</STARTING_FOLDER>
   <FOLDER_LOGIC>FULL</FOLDER_LOGIC>
   <IGNORE>
    <item>/.gitignore</item>
    <item>/LICENSE</item>
    <item>/README.md</item>
    <item>/package.json</item>
    <item>/.travis.yml</item>
   </IGNORE>
  </DATA>
 </asx:values>
</asx:abap>''')

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
