"""
ADT proxy for ababgit commands
"""

import time

import sap.adt.abapgit
import sap.cli.core
import sap.cli.helpers


class CommandGroup(sap.cli.core.CommandGroup):
    """Commands for ababgit"""

    def __init__(self):
        super().__init__('abapgit')


@CommandGroup.argument('--corrnr', type=str, nargs='?')
@CommandGroup.argument('--remote-user', type=str, nargs='?')
@CommandGroup.argument('--remote-password', type=str, nargs='?')
@CommandGroup.argument('--branch', type=str, nargs='?', default='refs/heads/master')
@CommandGroup.argument('url')
@CommandGroup.argument('package')
@CommandGroup.command()
def link(connection, args):
    """ link git repository to ABAP package
    """

    resp = sap.adt.abapgit.Repository.link(connection, {
        'package': args.package.upper(),
        'url': args.url,
        'branchName': args.branch,
        'remoteUser': args.remote_user,
        'remotePassword': args.remote_password,
        'transportRequest': args.corrnr
    })

    console = sap.cli.core.get_console()
    if resp.status_code == 200:
        console.printout('Repository was linked.')
    else:
        console.printerr(f'Failed to link repository: {args.package}', resp)


@ CommandGroup.argument('--corrnr', type=str, nargs='?')
@ CommandGroup.argument('--branch', type=str, nargs='?', default=None)
@ CommandGroup.argument('--remote-user', type=str, nargs='?')
@ CommandGroup.argument('--remote-password', type=str, nargs='?')
@ CommandGroup.argument('package')
@ CommandGroup.command()
def pull(connection, args):
    """ pull git repository branch to linked ABAP package
    """

    repository = sap.adt.abapgit.Repository(connection, args.package.upper())
    repository.fetch()
    repository.pull({
        'branchName': args.branch,
        'remoteUser': args.remote_user,
        'remotePassword': args.remote_password,
        'transportRequest': args.corrnr
    })

    repository.fetch()
    console = sap.cli.core.get_console()
    with sap.cli.helpers.ConsoleHeartBeat(console, 1):
        while repository.get_status() == 'R':
            time.sleep(1)
            repository.fetch()

    if repository.get_status() == 'E' or repository.get_status() == 'A':
        console.printerr(repository.get_status_text())
        console.printerr(repository.get_error_log())
    else:
        console.printout(repository.get_status_text())
