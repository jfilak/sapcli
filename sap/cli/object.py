"""ADT Object CLI templates"""

import sys

import sap.cli.core

import sap.adt
import sap.adt.wb


class CommandGroupObjectTemplate(sap.cli.core.CommandGroup):
    """Template Class converting command line parameters to ADT Object methods
       calls.
    """

    def instance(self, connection, name, args, metadata=None):
        """Returns new instance of the ADT Object proxy class"""

        raise NotImplementedError()

    def build_new_metadata(self, connection, args):
        """Creates an instance of the ADT Object Metadata class for a new object"""

        raise NotImplementedError()

    def define_create(self, commands):
        """Declares the Create command with its parameters and returns
           the definition.

           Notice, that this command does not declare the parameter package
           which should be create by descendants if necessary.
        """

        create_cmd = commands.add_command(self.create_object, name='create')
        create_cmd.append_argument('name')
        create_cmd.append_argument('description')
        create_cmd.declare_corrnr()

        return create_cmd

    def define_read(self, commands):
        """Declares the Read command with its parameters and returns
           the definition
        """

        read_cmd = commands.add_command(self.read_object_text, name='read')
        read_cmd.append_argument('name')

        return read_cmd

    def define_write(self, commands):
        """Declares the Write command with its parameters and returns
           the definition.
        """

        write_cmd = commands.add_command(self.write_object_text, name='write')
        write_cmd.append_argument('name')
        write_cmd.append_argument('source', help='a path or - for stdin')
        write_cmd.declare_corrnr()

        return write_cmd

    def define_activate(self, commands):
        """Declares the Activate command with its parameters and returns the
           definition.

           Notice that it allows multiple names on input.
        """

        activate_cmd = commands.add_command(self.activate_objects, name='activate')
        activate_cmd.append_argument('name', nargs='+')

        return activate_cmd

    def define(self):
        """Defines the commands Create, Read, Write, and Activate and returns
           the command list
        """

        cls = self.__class__

        if hasattr(cls, '_instance'):
            return None

        # pylint: disable=protected-access
        cls._instance = self

        commands = cls.get_commands()

        self.define_create(commands)
        self.define_read(commands)
        self.define_write(commands)
        self.define_activate(commands)

        return commands

    def build_new_object(self, connection, args, metadata):
        """Creates an instance of the ADT Object proxy class for a new object"""

        return self.instance(connection, args.name, args, metadata=metadata)

    def create_object(self, connection, args):
        """Creates the given object."""

        metadata = self.build_new_metadata(connection, args)
        obj = self.build_new_object(connection, args, metadata)

        obj.description = args.description

        obj.create(corrnr=args.corrnr)

    def read_object_text(self, connection, args):
        """Retrieves the request command prints it out based on command line
           configuration.
        """

        obj = self.instance(connection, args.name, args)
        print(obj.text)

    def write_object_text(self, connection, args):
        """Changes source code of the given program include"""

        text = None

        if args.source == '-':
            text = sys.stdin.readlines()
        else:
            with open(args.source, 'r') as filesrc:
                text = filesrc.readlines()

        obj = self.instance(connection, args.name, args)

        with obj.open_editor(corrnr=args.corrnr) as editor:
            editor.write(''.join(text))

    def activate_objects(self, connection, args):
        """Actives the given object."""

        for name in args.name:
            obj = self.instance(connection, name, args)
            sap.adt.wb.activate(obj)


# pylint: disable=abstract-method
class CommandGroupObjectMaster(CommandGroupObjectTemplate):
    """Commands for objects that belongs to a package.

       The class CommandGroupObjectTemplate defines the command create without the
       parameter packages because there are objects that belongs to a container
       object (i.e. Function Module).
    """

    def build_new_metadata(self, connection, args):
        """Creates an instance of the ADT Object Metadata class for a new object"""

        return sap.adt.ADTCoreData(language='EN', master_language='EN',
                                   package=args.package.upper(), responsible=connection.user.upper())

    def define_create(self, commands):
        """Calls the super's define_create and inserts the parameter package
           right behind the parameter description
        """

        create_cmd = super(CommandGroupObjectMaster, self).define_create(commands)

        create_cmd.insert_argument(2, 'package')

        return create_cmd
