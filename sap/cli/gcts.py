"""gCTS methods"""

import sap.cli.core
import sap.rest.gcts


def print_gcts_message(console, log, prefix=' '):
    """Print out the message with its protocol if it exists."""

    if isinstance(log, str):
        message = log
    else:
        message = log.get('message', None)

    if message:
        console.printerr(prefix, message)
        prefix = prefix + '  '

    if not isinstance(log, dict):
        return

    try:
        protocol = log['protocol']
    except KeyError:
        return

    if isinstance(protocol, dict):
        protocol = [protocol]

    for protocol_item in protocol:
        print_gcts_message(console, protocol_item, prefix=prefix)


def dump_gcts_messages(console, messages):
    """Dumps gCTS exception to console"""

    console.printerr('Error Log:')
    for errmsg in messages['errorLog']:
        print_gcts_message(console, errmsg)

    console.printerr('Log:')
    for logmsg in messages['log']:
        print_gcts_message(console, logmsg)

    console.printerr('Exception:\n ', messages['exception'])


def print_gcts_commit(console, commit):
    """Prints out gCTS commit description"""

    console.printout('commit', commit['id'])
    console.printout('Author:', commit['author'], f'<{commit["authorMail"]}>')
    console.printout('Date:  ', commit['date'])
    console.printout('\n   ', commit['message'])


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

    try:
        response = sap.rest.gcts.simple_fetch_repos(connection)
    except sap.rest.gcts.GCTSRequestError as ex:
        dump_gcts_messages(console, ex.messages)
        return 1

    for repo in response:
        console.printout(repo.name, repo.branch, repo.head, repo.url)

    return 0


@CommandGroup.argument('--vsid', type=str, nargs='?', default='6IT')
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

    try:
        repo = sap.rest.gcts.simple_clone(connection, args.url, package,
                                          start_dir=args.starting_folder,
                                          vcs_token=args.vcs_token,
                                          vsid=args.vsid,
                                          error_exists=not args.no_fail_exists)
    except sap.rest.gcts.GCTSRequestError as ex:
        dump_gcts_messages(sap.cli.core.get_console(), ex.messages)
        return 1

    console = sap.cli.core.get_console()
    console.printout('Cloned repository:')
    console.printout(' URL   :', repo.url)
    console.printout(' branch:', repo.branch)
    console.printout(' HEAD  :', repo.head)

    return 0


@CommandGroup.argument('package')
@CommandGroup.argument('-l', '--list', default=False, action='store_true')
@CommandGroup.command()
def config(connection, args):
    """git config [-l] [<package>]
    """

    console = sap.cli.core.get_console()

    if args.list:
        repo = sap.rest.gcts.Repository(connection, args.package)

        try:
            configuration = repo.configuration
        except sap.rest.gcts.GCTSRequestError as ex:
            dump_gcts_messages(sap.cli.core.get_console(), ex.messages)
            return 1

        for key, value in configuration.items():
            console.printout(f'{key}={value}')

        return 0

    console.printerr('Invalid command line options\nRun: sapcli gcts config --help')
    return 1


@CommandGroup.argument('package')
@CommandGroup.command()
def delete(connection, args):
    """rm
    """

    try:
        sap.rest.gcts.simple_delete(connection, args.package)
    except sap.rest.gcts.GCTSRequestError as ex:
        dump_gcts_messages(sap.cli.core.get_console(), ex.messages)
        return 1

    sap.cli.core.printout(f'The repository "{args.package}" has been deleted')
    return 0


@CommandGroup.argument('branch')
@CommandGroup.argument('package')
@CommandGroup.command()
def checkout(connection, args):
    """git checkout <branch>
    """

    repo = sap.rest.gcts.Repository(connection, args.package)
    old_branch = repo.branch

    try:
        response = sap.rest.gcts.simple_checkout(connection, args.branch, repo=repo)
    except sap.rest.gcts.GCTSRequestError as ex:
        dump_gcts_messages(sap.cli.core.get_console(), ex.messages)
        return 1

    sap.cli.core.printout(f'The repository "{args.package}" has been set to the branch "{args.branch}"')
    sap.cli.core.printout(f'({old_branch}:{response["fromCommit"]}) -> ({args.branch}:{response["toCommit"]})')
    return 0


@CommandGroup.argument('package')
@CommandGroup.command('log')
def gcts_log(connection, args):
    """git log
    """

    console = sap.cli.core.get_console()
    try:
        commits = sap.rest.gcts.simple_log(connection, name=args.package)
    except sap.rest.gcts.GCTSRequestError as ex:
        dump_gcts_messages(console, ex.messages)
        return 1

    if not commits:
        return 0

    commit_iter = iter(commits)

    commit = next(commit_iter)
    print_gcts_commit(console, commit)

    for commit in commit_iter:
        console.printout('')
        print_gcts_commit(console, commit)

    return 0
