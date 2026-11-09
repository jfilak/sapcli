"""ADT proxy for BAdI Enhancement Implementation (ENHO/XHB) commands"""

import sap.adt
import sap.cli.object


class CommandGroup(sap.cli.object.CommandGroupObjectMaster):
    """Commands for BAdI Enhancement Implementations (ENHO);
       use the command badi to work with BAdI Implementations
       of an Enhancement Implementation
    """

    def __init__(self):
        super().__init__('enho', description=CommandGroup.__doc__)

        self.define()

    def instance(self, connection, name, args, metadata=None):
        package = None
        if hasattr(args, 'package'):
            package = args.package.upper()

        return sap.adt.EnhancementImplementation(connection, name.upper(), package=package, metadata=metadata)

    def build_new_object(self, connection, args, metadata):
        obj = super().build_new_object(connection, args, metadata)
        obj.set_enhancement_spot(args.enhancement_spot.upper())

        return obj

    def define_create(self, commands):
        create_cmd = commands.add_command(
            self.create_object, name='create',
            description='Create a new BAdI Enhancement Implementation of the given Enhancement Spot'
                        ' without any BAdI Implementation')
        create_cmd.append_argument('name', help='Enhancement Implementation name')
        create_cmd.append_argument('description', help='Enhancement Implementation description')
        create_cmd.append_argument('package', help='Package of the new Enhancement Implementation')
        create_cmd.append_argument('-s', '--enhancement-spot', required=True,
                                   help='Enhancement Spot whose BAdI Definitions will be implemented')
        create_cmd.declare_corrnr()

        return create_cmd

    def define(self):
        """Defines only the commands working with the object as a whole
           because Enhancement Implementation has no source code.
        """

        cls = self.__class__

        if hasattr(cls, '_instance'):
            return None

        # pylint: disable=protected-access
        cls._instance = self

        commands = cls.get_commands()

        self.define_create(commands)
        self.define_activate(commands)
        self.define_delete(commands)
        self.define_whereused(commands)

        return commands
