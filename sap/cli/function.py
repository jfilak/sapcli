"""ADT proxy for ABAP Functions"""

import argparse
import os
from typing import Optional

import sap.adt
import sap.cli.object
from sap.adt.core import Connection


def get_group(connection: Connection, args: argparse.Namespace, name: Optional[str] = None) -> str:
    """Returns the function group name from args, resolving it via search
       if the user passed '-' instead of a group name.

       :param name: optional explicit function module name to search for;
                    if not provided, args.name is used (must be a string)
    """

    if args.group == '-':
        if name is None:
            name = args.name
        return sap.adt.FunctionModule.resolve_group(connection, name)

    return args.group


class CommandGroupFunctionGroupInclude(sap.cli.object.CommandGroupObjectTemplate):
    """Container for definition commands."""

    def __init__(self):
        super().__init__('include')

        self.define()

    def build_new_metadata(self, connection, args):
        return sap.adt.ADTCoreData(language='EN', master_language='EN',
                                   responsible=connection.user.upper())

    def build_new_object(self, connection, args, metadata):
        return sap.adt.FunctionInclude(connection, args.name.upper(), args.group, metadata=metadata)

    def instance(self, connection, name, args, metadata=None):
        return sap.adt.FunctionInclude(connection, name.upper(), args.group, metadata=metadata)

    def define_create(self, commands):
        create_cmd = super().define_create(commands)

        # Function Modules belong to a function group and not into a package!
        create_cmd.insert_argument(0, 'group')

        return create_cmd

    def define_read(self, commands):
        read_cmd = super().define_read(commands)

        # Function Modules belong to a function group and not into a package!
        read_cmd.insert_argument(0, 'group')

        return read_cmd

    def define_write(self, commands):
        write_cmd = super().define_write(commands)

        # Function Modules belong to a function group and not into a package!
        write_cmd.insert_argument(0, 'group')

        return write_cmd

    def define_activate(self, commands):
        activate_cmd = super().define_activate(commands)

        # Function Modules belong to a function group and not into a package!
        activate_cmd.insert_argument(0, 'group')

        return activate_cmd


class CommandGroupFunctionGroup(sap.cli.object.CommandGroupObjectMaster):
    """Commands for Function Groups"""

    def __init__(self):
        super().__init__('functiongroup')

        self.function_group_include_grp = CommandGroupFunctionGroupInclude()

        self.define()

    def install_parser(self, arg_parser):
        activation_group = super().install_parser(arg_parser)

        function_group_include_parser = activation_group.add_parser(self.function_group_include_grp.name)
        self.function_group_include_grp.install_parser(function_group_include_parser)

    def build_new_object(self, connection, args, metadata):
        return sap.adt.FunctionGroup(connection, args.name.upper(), package=args.package, metadata=metadata)

    def instance(self, connection, name, args, metadata=None):
        return sap.adt.FunctionGroup(connection, name.upper(), metadata=metadata)


class CommandGroupFunctionModule(sap.cli.object.CommandGroupObjectTemplate):
    """Commands for Function Modules"""

    def __init__(self):
        super().__init__('functionmodule')

        self.define()

    def build_new_metadata(self, connection, args):
        return sap.adt.ADTCoreData(language='EN', master_language='EN',
                                   responsible=connection.user.upper())

    def instance(self, connection: Connection, name: str, args: argparse.Namespace,
                 metadata: Optional[sap.adt.ADTCoreData] = None) -> sap.adt.FunctionModule:
        group = get_group(connection, args, name=name)
        return sap.adt.FunctionModule(connection, name.upper(), group, metadata=metadata)

    def instance_from_file_path(self, connection: Connection, filepath: str,
                                args: argparse.Namespace,
                                metadata: Optional[sap.adt.ADTCoreData] = None) -> sap.adt.FunctionModule:
        basename = os.path.basename(filepath)
        parts = basename.split('.', 3)

        if len(parts) < 4 or not parts[0] or parts[1].lower() != 'fugr' or not parts[2] or parts[3].lower() != 'abap':
            raise sap.cli.core.InvalidCommandLineError(
                f'"{basename}" does not match the pattern FUNCTIONGROUP.fugr.FUNCTIONMODULE.abap')

        group = parts[0]
        name = parts[2]
        return sap.adt.FunctionModule(connection, name.upper(), group, metadata=metadata)

    def define_create(self, commands):
        create_cmd = super().define_create(commands)

        # Function Modules belong to a function group and not into a package!
        create_cmd.insert_argument(0, 'group')

        return create_cmd

    def define_read(self, commands):
        read_cmd = super().define_read(commands)

        # Function Modules belong to a function group and not into a package!
        read_cmd.insert_argument(0, 'group')

        return read_cmd

    def define_write(self, commands):
        write_cmd = super().define_write(commands)

        # Function Modules belong to a function group and not into a package!
        write_cmd.insert_argument(0, 'group')

        return write_cmd

    def define_activate(self, commands):
        activate_cmd = super().define_activate(commands)

        # Function Modules belong to a function group and not into a package!
        activate_cmd.insert_argument(0, 'group')

        return activate_cmd


@CommandGroupFunctionModule.argument_corrnr()
@CommandGroupFunctionModule.argument('-t', '--processing_type', choices=['rfc', 'normal'])
@CommandGroupFunctionModule.argument('name')
@CommandGroupFunctionModule.argument('group')
@CommandGroupFunctionModule.command()
def chattr(connection: Connection, args: argparse.Namespace) -> None:
    """Changes attributes of the given Function Module"""

    group = get_group(connection, args)
    fmodule = sap.adt.FunctionModule(connection, args.name.upper(), group)
    fmodule.fetch()

    if hasattr(args, 'processing_type'):
        fmodule.processing_type = args.processing_type  # type: ignore[method-assign]

    with fmodule.open_editor(corrnr=args.corrnr) as editor:
        editor.push()
