"""ABAP User handling methods"""

import sap.cli.core
import sap.cli.helpers
import sap.rfc.user


class CommandGroup(sap.cli.core.CommandGroup):
    """Adapter converting command line parameters to sap.rfc.user
       methods calls.
    """

    def __init__(self):
        super().__init__('user')


@CommandGroup.argument('username')
@CommandGroup.command()
def details(connection, args):
    """Dump user details"""

    manager = sap.rfc.user.UserManager()
    rfc_details = manager.fetch_user_details(connection, args.username)
    sap.cli.core.printout('User      :', args.username)
    sap.cli.core.printout('Alias     :', rfc_details['ALIAS']['USERALIAS'])
    sap.cli.core.printout('Last Login:', rfc_details['LOGONDATA']['LTIME'])


@CommandGroup.argument('--type', choices=['Dialog', 'Service', 'System'], default='Dialog')
@CommandGroup.argument('--new-password', nargs='?')
@CommandGroup.argument('username')
@CommandGroup.command()
def create(connection, args):
    """Dump user details"""

    manager = sap.rfc.user.UserManager()

    builder = manager.user_builder()
    builder.set_username(args.username)
    builder.set_type(args.type)
    builder.set_password(args.new_password)

    sap.cli.core.printout(manager.create_user(connection, builder))


@CommandGroup.argument('--new-password', nargs='?')
@CommandGroup.argument('username')
@CommandGroup.command()
def change(connection, args):
    """Dump user details"""

    manager = sap.rfc.user.UserManager()

    builder = manager.user_builder()
    builder.set_username(args.username)
    builder.set_password(args.new_password)

    sap.cli.core.printout(manager.change_user(connection, builder))
