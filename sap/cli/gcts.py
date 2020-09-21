"""gCTS methods"""

import sap.cli.core
import sap.rest.gcts


class CommandGroup(sap.cli.core.CommandGroup):
    """Adapter converting command line parameters to sap.rest.gcts
       methods calls.
    """

    def __init__(self):
        super().__init__('gcts')


@CommandGroup.command()
# pylint: disable=unused-argument
def repolist(connection, args):
    """ls"""

    console = sap.cli.core.get_console()

    response = sap.rest.gcts.simple_fetch_repos(connection)
    for repo in response:
        console.printout(repo.name, repo.branch, repo.url)


@CommandGroup.argument('--starting-folder', type=str, nargs='?', default='src/')
@CommandGroup.argument('--no-fail-exists', default=False, action='store_true')
@CommandGroup.argument('--vcs-token', type=str, nargs='?')
@CommandGroup.argument('package', nargs='?')
@CommandGroup.argument('url')
@CommandGroup.command()
def clone(connection, args):
    """git clone <repository> [<package>]
    """

    package = args.package
    if not package:
        package = sap.rest.gcts.package_name_from_url(args.url)

    sap.rest.gcts.simple_clone(connection, args.url, package,
                               start_dir=args.starting_folder,
                               vcs_token=args.vcs_token)


@CommandGroup.argument('package')
@CommandGroup.argument('-l', '--list', default=False, action='store_true')
@CommandGroup.command()
def config(connection, args):
    """git config [-l] [<package>]
    """

    console = sap.cli.core.get_console()

    if args.list:
        repo = sap.rest.gcts.Repository(connection, args.package)
        for key, value in repo.configuration.items():
            console.printout(f'{key}={value}')

        return 0

    console.printerr('Invalid command line options\nRun: sapcli gcts config --help')
    return 1


@CommandGroup.argument('package')
@CommandGroup.command()
def delete(connection, args):
    """rm
    """

    sap.rest.gcts.simple_delete(connection, args.package)
    sap.cli.core.printout(f'The repository "{args.package}" has been deleted')


@CommandGroup.argument('branch')
@CommandGroup.argument('package')
@CommandGroup.command()
def checkout(connection, args):
    """git checkout <branch>
    """

    sap.rest.gcts.simple_checkout(connection, args.package, args.branch)
    sap.cli.core.printout(f'The repository "{args.package}" has been set to the branch "{args.branch}"')
