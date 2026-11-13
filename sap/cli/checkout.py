"""ADT Object export"""
import os
import sys

import sap.adt
import sap.adt.textelements
import sap.cli.core
from sap.cli.localrepo import OBJECT_HANDLERS, REPOSITORY_LAYOUT
from sap.fileformat.abapgit.fugr import SourceCodeFormat, checkout_function_group


class CommandGroup(sap.cli.core.CommandGroup):
    """Commands for exporting ADT objects"""

    def __init__(self):
        super().__init__('checkout')


def _checkout_object(connection, adt_type, name):
    """Checks out the object to the current directory"""

    OBJECT_HANDLERS.for_adt_type(adt_type).checkout(connection, adt_type, name.upper(), None)


@CommandGroup.argument('name')
@CommandGroup.command('class')
def abapclass(connection, args):
    """Download all class sources command wrapper"""

    _checkout_object(connection, sap.adt.Class.OBJTYPE.code, args.name)


@CommandGroup.argument('name')
@CommandGroup.command()
def program(connection, args):
    """Download program sources command wrapper"""

    _checkout_object(connection, sap.adt.Program.OBJTYPE.code, args.name)


@CommandGroup.argument('name')
@CommandGroup.command()
def interface(connection, args):
    """Download interface sources command wrapper"""

    _checkout_object(connection, sap.adt.Interface.OBJTYPE.code, args.name)


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


@CommandGroup.argument('name')
@CommandGroup.command()
def tabletype(connection, args):
    """Download table type attributes command wrapper"""

    _checkout_object(connection, sap.adt.TableType.OBJTYPE.code, args.name)


@CommandGroup.argument('name')
@CommandGroup.command('ddl')
def datadefinition(connection, args):
    """Download data definition source code and attributes command wrapper"""

    _checkout_object(connection, sap.adt.DataDefinition.OBJTYPE.code, args.name)


@CommandGroup.argument('name')
@CommandGroup.command('dcl')
def accesscontrol(connection, args):
    """Download access control source code and attributes command wrapper"""

    _checkout_object(connection, sap.adt.AccessControl.OBJTYPE.code, args.name)


@CommandGroup.argument('name')
@CommandGroup.command('ddlx')
def metadataextension(connection, args):
    """Download metadata extension source code and attributes command wrapper"""

    _checkout_object(connection, sap.adt.MetadataExtension.OBJTYPE.code, args.name)


@CommandGroup.argument('name')
@CommandGroup.command('bdef')
def behaviordefinition(connection, args):
    """Download behavior definition source code and attributes command wrapper"""

    _checkout_object(connection, sap.adt.BehaviorDefinition.OBJTYPE.code, args.name)


@CommandGroup.argument('name')
@CommandGroup.command()
def table(connection, args):
    """Download table attributes command wrapper"""

    _checkout_object(connection, sap.adt.Table.OBJTYPE.code, args.name)


@CommandGroup.argument('name')
@CommandGroup.command()
def structure(connection, args):
    """Download structure attributes command wrapper"""

    _checkout_object(connection, sap.adt.Structure.OBJTYPE.code, args.name)


@CommandGroup.argument('name')
@CommandGroup.command()
def domain(connection, args):
    """Download domain attributes command wrapper"""

    _checkout_object(connection, sap.adt.Domain.OBJTYPE.code, args.name)


@CommandGroup.argument('name')
@CommandGroup.command()
def dataelement(connection, args):
    """Download data element attributes command wrapper"""

    _checkout_object(connection, sap.adt.DataElement.OBJTYPE.code, args.name)


def checkout_objects(connection, objects, destdir=None):
    """Checkout all objects from the give list"""

    if not os.path.isdir(destdir):
        os.makedirs(destdir)

    for obj in objects:
        handler = OBJECT_HANDLERS.for_adt_type(obj.typ)
        if handler is None:
            print(f'Unsupported object: {obj.typ} {obj.name}', file=sys.stderr)
            continue

        # Errors are reported by raising an SAPCliError because the command
        # line entry point prints out human friendly text.
        handler.checkout(connection, obj.typ, obj.name, destdir)


def make_repo_dir_for_package(args):
    """Creates and populates the directory to checkout the package into."""

    repo_dir = args.directory
    if not repo_dir:
        repo_dir = args.name

    repo_dir = os.path.abspath(repo_dir)

    if not os.path.isdir(repo_dir):
        os.makedirs(repo_dir)

    REPOSITORY_LAYOUT.init_repository(repo_dir, args.starting_folder)

    return repo_dir


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
        REPOSITORY_LAYOUT.checkout_package(connection, package_name.upper(), destdir)

        if not args.recursive:
            break
