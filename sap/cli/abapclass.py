"""ADT proxy for ABAP Class (OO)"""

import sap.adt
import sap.adt.textelements
import sap.adt.wb
import sap.cli.core
import sap.cli.object


SOURCE_TYPES = ['main', 'definitions', 'implementations', 'testclasses', 'textelements']

FILE_NAME_SUFFIX_TYPES = {
    'clas.abap': None,
    'clas.locals_def.abap': 'definitions',
    'clas.testclasses.abap': 'testclasses',
    'clas.locals_imp.abap': 'implementations'
}


def instance_from_args(connection, name, typ, args, metadata):
    """Converts command line arguments to an instance of an ADT class
       based on the given typ.
    """

    package = None
    if hasattr(args, 'package'):
        package = args.package

    clas = sap.adt.Class(connection, name.upper(), package=package, metadata=metadata)

    if typ == 'definitions':
        return clas.definitions

    if typ == 'implementations':
        return clas.implementations

    if typ == 'testclasses':
        return clas.test_classes

    if typ == 'textelements':
        return sap.adt.textelements.ClassTextElements(connection, name.upper())

    return clas


class CommandGroup(sap.cli.object.CommandGroupObjectMaster):
    """Commands for Class"""

    def __init__(self):
        super().__init__('class')

        self.define()

    def instance(self, connection, name, args, metadata=None):
        typ = None
        if hasattr(args, 'type'):
            typ = args.type

        return instance_from_args(connection, name, typ, args, metadata)

    def instance_from_file_path(self, connection, filepath, args, metadata=None):
        name, suffix = sap.cli.object.object_name_from_source_file(filepath)

        try:
            typ = FILE_NAME_SUFFIX_TYPES[suffix]
        except KeyError as ex:
            raise sap.cli.core.InvalidCommandLineError(f'Unknown class file name suffix: "{suffix}"') from ex

        return instance_from_args(connection, name, typ, args, metadata)

    def _save_object_text(self, obj, code, check_before_save, corrnr=None, editor=None):
        if not isinstance(obj, sap.adt.textelements.ClassTextElements):
            super()._save_object_text(obj, code, check_before_save, corrnr=corrnr, editor=editor)
            return

        # Text symbols are not ABAP source code, so abapCheckRun cannot check them
        if editor is not None:
            editor.write(code)
        else:
            with obj.open_editor(corrnr=corrnr) as new_editor:
                new_editor.write(code)

    def define_read(self, commands):
        read_cmd = super().define_read(commands)
        read_cmd.insert_argument(1, '--type', default=SOURCE_TYPES[0], choices=SOURCE_TYPES)

        return read_cmd

    def define_write(self, commands):
        write_cmd = super().define_write(commands)
        write_cmd.insert_argument(1, '--type', default=SOURCE_TYPES[0], choices=SOURCE_TYPES)

        return write_cmd


@CommandGroup.argument('name')
@CommandGroup.command()
def attributes(connection, args):
    """Prints out some attributes of the given class.
    """

    clas = sap.adt.Class(connection, args.name.upper())
    clas.fetch()

    print(f'Name       : {clas.name}')
    print(f'Description: {clas.description}')
    print(f'Responsible: {clas.responsible}')
    # pylint: disable=no-member
    print(f'Package    : {clas.reference.name}')


@CommandGroup.argument('name')
@CommandGroup.command()
def execute(connection, args):
    """Runs the if_oo_adt_classrun~main method"""

    clas = sap.adt.Class(connection, args.name.upper())
    print(clas.execute())
