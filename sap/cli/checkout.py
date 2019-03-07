"""ADT Object export"""

import sys

import sap.adt
import sap.cli.core


class CommandGroup(sap.cli.core.CommandGroup):
    """Commands for exporting ADT objects"""

    def __init__(self):
        super(CommandGroup, self).__init__('checkout')


def download_abap_source(object_name, source_object, typsfx):
    """Reads the text and saves it in the corresponding file"""

    filename = f'{object_name}{typsfx}.abap'
    with open(filename.lower(), 'w') as dest:
        dest.write(source_object.text)


def checkout_class(connection, name):
    """Download entire class"""

    clas = sap.adt.Class(connection, name)

    download_abap_source(name, clas, '.clas')
    download_abap_source(name, clas.definitions, '.clas.locals_def')
    download_abap_source(name, clas.implementations, '.clas.locals_imp')
    download_abap_source(name, clas.test_classes, '.clas.testclasses')


@CommandGroup.command('class')
@CommandGroup.argument('name')
def abapclass(connection, args):
    """Download all class sources command wrapper"""

    checkout_class(connection, args.name)


def checkout_program(connection, name):
    """Download program sources"""

    download_abap_source(name, sap.adt.Program(connection, name), '.prog')


@CommandGroup.command()
@CommandGroup.argument('name')
def program(connection, args):
    """Download program sources command wrapper"""

    checkout_program(connection, args.name)


def checkout_interface(connection, name):
    """Download interface sources"""

    download_abap_source(name, sap.adt.Interface(connection, name), '.intf')


@CommandGroup.command()
@CommandGroup.argument('name')
def interface(connection, args):
    """Download interface sources command wrapper"""

    checkout_interface(connection, args.name)


@CommandGroup.command()
# @CommandGroup.argument('--folder-logic', choices=['full', 'prefix'], default='prefix')
# @CommandGroup.argument('--recursive', action='store_true', default=False)
# @CommandGroup.argument('--starting-folder', default='src')
@CommandGroup.argument('name')
def package(connection, args):
    """Download sources of objects from the given ABAP package"""

    checkouters = {
        'PROG/P': checkout_program,
        'CLAS/OC': checkout_class,
        'INTF/OI': checkout_interface,
    }

    explored = sap.adt.Package(connection, args.name)

    _, subpackages, objects = next(sap.adt.package.walk(explored))

    for subpkg in subpackages:
        print(f'Ignoring sub-package: {subpkg}', file=sys.stderr)

    for obj in objects:
        try:
            checkouters[obj.typ](connection, obj.name)
        except KeyError:
            print(f'Unsupported object: {obj.typ} {obj.name}', file=sys.stderr)
