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
def repolist(connection, args):
    """ls"""

    response = sap.rest.gcts.simple_fetch_repos(connection)
    for repo in response:
        print(repo['name'], repo['branch'], repo['url'])


@CommandGroup.argument('--starting-folder', type=str, nargs='?', default='src')
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

    response = sap.rest.gcts.simple_clone(connection, args.url, package,
                                          start_dir=args.starting_folder,
                                          vcs_token=args.vcs_token)
    print(response)


@CommandGroup.argument('package')
@CommandGroup.command()
def delete(connection, args):
    """rm
    """

    response = sap.rest.gcts.simple_delete(connection, args.package)
    print(response)


@CommandGroup.argument('branch')
@CommandGroup.argument('package')
@CommandGroup.command()
def checkout(connection, args):
    """git checkout <branch>
    """

    response = sap.rest.gcts.simple_checkout(connection, args.package, args.branch)
    print(response)


@CommandGroup.argument('url')
@CommandGroup.argument('package')
@CommandGroup.command()
def init(connection, args):
    """git init <package>
       git remote add origin <url>
    """

    pass


@CommandGroup.argument('pathspec', nargs='+')
@CommandGroup.argument('package')
@CommandGroup.command()
def add(connection, args):
    """git add <pathspec>
    """

    pass
