"""Command line interface for Message Class ADT objects"""

import json

import sap.adt
import sap.adt.messageclass
import sap.cli.object
from sap.errors import SAPCliError
from sap.platform.abap.fileformats.messageclass import to_json


class MessageCommandGroup(sap.cli.object.CommandGroupObjectTemplate):
    """Commands for individual messages within a message class"""

    def __init__(self):
        super().__init__('message')

        self.define()

    def instance(self, connection, name, args, metadata=None):
        return sap.adt.MessageClass(connection, name.upper(), metadata=metadata)

    def build_new_metadata(self, connection, args):
        return sap.adt.ADTCoreData(language='EN', master_language='EN',
                                   responsible=connection.user.upper())

    def define_create(self, commands):
        create_cmd = commands.add_command(self.message_create, name='create')
        create_cmd.append_argument('name', help='Message class name')
        create_cmd.append_argument('msgno', help='Message number (3 digits)')
        create_cmd.append_argument('msgtext', help='Message text')
        create_cmd.append_argument('--selfexplanatory', choices=['true', 'false'], default='false',
                                   help='Whether the message is self-explanatory')
        create_cmd.declare_corrnr()

        return create_cmd

    def define_read(self, commands):
        read_cmd = commands.add_command(self.message_read, name='read')
        read_cmd.append_argument('name', help='Message class name')
        read_cmd.append_argument('msgno', help='Message number (3 digits)')

        return read_cmd

    def define_write(self, commands):
        write_cmd = commands.add_command(self.message_write, name='write')
        write_cmd.append_argument('name', help='Message class name')
        write_cmd.append_argument('msgno', help='Message number (3 digits)')
        write_cmd.append_argument('msgtext', help='Message text')
        write_cmd.append_argument('--selfexplanatory', choices=['true', 'false'], default='false',
                                  help='Whether the message is self-explanatory')
        write_cmd.declare_corrnr()

        return write_cmd

    def define_activate(self, commands):
        # Messages don't need activation - skip
        return None

    def define_delete(self, commands):
        delete_cmd = commands.add_command(self.message_delete, name='delete')
        delete_cmd.append_argument('name', help='Message class name')
        delete_cmd.append_argument('msgno', help='Message number (3 digits)')
        delete_cmd.declare_corrnr()

        return delete_cmd

    def define_whereused(self, commands):
        # Not applicable for individual messages
        return None

    def define(self):
        cls = self.__class__

        if hasattr(cls, '_instance'):
            return None

        # pylint: disable=protected-access
        cls._instance = self

        commands = cls.get_commands()

        self.define_create(commands)
        self.define_read(commands)
        self.define_write(commands)
        self.define_delete(commands)

        return commands

    def message_create(self, connection, args):
        """Create a new message in a message class"""

        msgclass = sap.adt.MessageClass(connection, args.name)
        msgclass.set_message(connection, args.msgno, args.msgtext,
                             selfexplainatory=args.selfexplanatory, corrnr=args.corrnr)

    def message_write(self, connection, args):
        """Write (update) a message in a message class"""

        msgclass = sap.adt.MessageClass(connection, args.name)
        msgclass.set_message(connection, args.msgno, args.msgtext,
                             selfexplainatory=args.selfexplanatory, corrnr=args.corrnr)

    def message_read(self, connection, args):
        """Read a single message from a message class"""

        console = args.console_factory()
        msgclass = sap.adt.MessageClass(connection, args.name)
        msgclass.fetch()

        for msg in msgclass.messages:
            if msg.msgno == args.msgno:
                console.printout(f'Number: {msg.msgno}')
                console.printout(f'Text  : {msg.msgtext}')
                console.printout(f'S./Ex.: {msg.selfexplainatory}')
                return

        raise SAPCliError(f'Message {args.msgno} not found in message class {args.name}')

    def message_delete(self, connection, args):
        """Delete a message from a message class"""

        msgclass = sap.adt.MessageClass(connection, args.name)
        msgclass.delete_message(connection, args.msgno, corrnr=args.corrnr)


class CommandGroup(sap.cli.object.CommandGroupObjectMaster):
    """Commands for Message Class objects"""

    def __init__(self):
        super().__init__('messageclass')

        self.message_grp = MessageCommandGroup()

        self.define()

    def install_parser(self, arg_parser):
        activation_group = super().install_parser(arg_parser)

        message_parser = activation_group.add_parser(self.message_grp.name)
        self.message_grp.install_parser(message_parser)

    def instance(self, connection, name, args, metadata=None):
        return sap.adt.MessageClass(connection, name.upper(), metadata=metadata)

    def build_new_object(self, connection, args, metadata):
        return sap.adt.MessageClass(connection, args.name.upper(),
                                    package=args.package, metadata=metadata)

    def define_read(self, commands):
        read_cmd = commands.add_command(self.read_messageclass, name='read')
        read_cmd.append_argument('name')
        read_cmd.append_argument('--output', choices=['JSON', 'HUMAN'], default='HUMAN',
                                 help='Output format')

        return read_cmd

    def define_write(self, commands):
        write_cmd = commands.add_command(self.write_messageclass, name='write')
        write_cmd.append_argument('name')

        return write_cmd

    def define_activate(self, commands):
        activate_cmd = commands.add_command(self.activate_messageclass, name='activate')
        activate_cmd.append_argument('name')

        return activate_cmd

    def read_messageclass(self, connection, args):
        """Read a message class"""

        console = args.console_factory()
        msgclass = sap.adt.MessageClass(connection, args.name)
        msgclass.fetch()

        if args.output == 'JSON':
            result = to_json(msgclass)
            console.printout(json.dumps(result, indent=4))
        else:
            _print_human(console, msgclass)

    def write_messageclass(self, connection, args):  # pylint: disable=unused-argument
        """Write a message class (Not implemented yet)"""

        console = args.console_factory()
        console.printout('Not implemented yet')

    def activate_messageclass(self, connection, args):  # pylint: disable=unused-argument
        """Activate a message class"""

        console = args.console_factory()
        console.printout('Message classes do not require activation')


def _print_human(console, msgclass):
    """Print message class in human-readable table format"""

    console.printout(f'Description: {msgclass.description}')
    console.printout('')

    if not msgclass.messages:
        console.printout('No messages.')
        return

    # Find longest text for column width
    max_text_len = max(len(msg.msgtext or '') for msg in msgclass.messages)
    max_text_len = max(max_text_len, len('Text'))

    header = f'No. | {"Text":<{max_text_len}} | Selfexplanatory'
    separator = f'----|{"-" * (max_text_len + 2)}|----------------'

    console.printout(header)
    console.printout(separator)

    for msg in msgclass.messages:
        text = msg.msgtext or ''
        selfexp = msg.selfexplainatory or 'false'
        console.printout(f'{msg.msgno} | {text:<{max_text_len}} | {selfexp}')
