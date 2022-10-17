"""gCTS methods"""

import warnings

import sap.cli.core
import sap.cli.helpers
import sap.rest.gcts.simple
from sap.rest.gcts.remote_repo import (
    Repository,
    RepoActivitiesQueryParams,
)
from sap.rest.gcts.errors import (
    GCTSRequestError,
    SAPCliError,
)


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

    output = False
    errlog = messages.get('errorLog', None)
    if errlog:
        output = True
        console.printerr('Error Log:')
        for errmsg in errlog:
            print_gcts_message(console, errmsg)

    msglog = messages.get('log', None)
    if msglog:
        output = True
        console.printerr('Log:')
        for logmsg in msglog:
            print_gcts_message(console, logmsg)

    exception = messages.get('exception', None)
    if exception:
        output = True
        console.printerr('Exception:\n ', messages['exception'])

    if not output:
        console.printerr(str(messages))


def print_gcts_commit(console, commit_data):
    """Prints out gCTS commit description"""

    console.printout('commit', commit_data['id'])
    console.printout('Author:', commit_data['author'], f'<{commit_data["authorMail"]}>')
    console.printout('Date:  ', commit_data['date'])
    console.printout('\n   ', commit_data['message'])


def get_repository(connection, package):
    """Get repository corresponding to the PACKAGE"""

    if package.startswith(('http://', 'https://')):
        repositories = sap.rest.gcts.simple.fetch_repos(connection)
        repositories = [repo for repo in repositories if repo.url == package]

        if not repositories:
            raise SAPCliError(f'No repository found with the URL "{package}".')

        if len(repositories) > 1:
            raise SAPCliError(f'Cannot uniquely identify the package based on the URL "{package}".')

        return repositories[0]

    return Repository(connection, package)


class UserCommandGroup(sap.cli.core.CommandGroup):
    """Container for user commands."""

    def __init__(self):
        super().__init__('user')


@UserCommandGroup.argument('-f', '--format', choices=['HUMAN', 'JSON'], default='HUMAN')
@UserCommandGroup.command('get-credentials')
def get_user_credentials(connection, args):
    """Get user credentials"""

    user_credentials = sap.rest.gcts.simple.get_user_credentials(connection)
    console = sap.cli.core.get_console()
    if args.format == 'JSON':
        console.printout(user_credentials)
    else:
        columns = (
            sap.cli.helpers.TableWriter.Columns()
            ('endpoint', 'Endpoint')
            ('type', 'Type')
            ('state', 'State')
            .done()
        )

        sap.cli.helpers.TableWriter(user_credentials, columns).printout(console)


@UserCommandGroup.argument('-t', '--token')
@UserCommandGroup.argument('-a', '--api-url')
@UserCommandGroup.command('set-credentials')
def set_user_credentials(connection, args):
    """Set user credentials"""

    sap.rest.gcts.simple.set_user_api_token(connection, args.api_url, args.token)


@UserCommandGroup.argument('-a', '--api-url')
@UserCommandGroup.command('delete-credentials')
def delete_user_credentials(connection, args):
    """Delete user credentials"""

    sap.rest.gcts.simple.delete_user_credentials(connection, args.api_url)


class PropertyCommandGroup(sap.cli.core.CommandGroup):
    """Container for property commands."""

    def __init__(self):
        super().__init__('property')


@PropertyCommandGroup.argument('package')
@PropertyCommandGroup.command('get')
def get_properties(connection, args):
    """Get all repository properties"""

    console = sap.cli.core.get_console()
    try:
        repo = get_repository(connection, args.package)

        console.printout(f'Name: {repo.name}')
        console.printout(f'RID: {repo.rid}')
        console.printout(f'Branch: {repo.branch}')
        console.printout(f'Commit: {repo.head}')
        console.printout(f'Status: {repo.status}')
        console.printout(f'vSID: {repo.vsid}')
        console.printout(f'Role: {repo.role}')
        console.printout(f'URL: {repo.url}')
    except SAPCliError as ex:
        console.printout(str(ex))
        return 1

    return 0


@PropertyCommandGroup.argument('value')
@PropertyCommandGroup.argument('property_name')
@PropertyCommandGroup.argument('package')
@PropertyCommandGroup.command('set')
def set_properties(connection, args):
    """Set the property of repository"""

    try:
        repo = get_repository(connection, args.package)
        repo.set_item(args.property_name.lower(), args.value)
    except SAPCliError as ex:
        sap.cli.core.printout(str(ex))
        return 1

    return 0


class BranchCommandGroup(sap.cli.core.CommandGroup):
    """Container for branch commands"""

    def __init__(self):
        super().__init__('branch')


@BranchCommandGroup.argument('-f', '--format', type=str, choices=['HUMAN', 'JSON'], default='HUMAN')
@BranchCommandGroup.argument('--local-only', default=False, action='store_true')
@BranchCommandGroup.argument('--peeled', default=False, action='store_true')
@BranchCommandGroup.argument('--symbolic', default=False, action='store_true')
@BranchCommandGroup.argument('name')
@BranchCommandGroup.argument('package')
@BranchCommandGroup.command('create')
def create_branch(connection, args):
    """Create new branch in repository"""

    console = sap.cli.core.get_console()
    try:
        repo = get_repository(connection, args.package)
        response = repo.create_branch(args.name, symbolic=args.symbolic, peeled=args.peeled, local_only=args.local_only)
    except GCTSRequestError as ex:
        dump_gcts_messages(console, ex.messages)
        return 1
    except SAPCliError as ex:
        console.printerr(str(ex))
        return 1

    if args.format.upper() == 'JSON':
        console.printout(sap.cli.core.json_dumps(response))
    else:
        console.printout(f'Branch "{response["name"]}" was created and now is active branch.')

    return 0


@BranchCommandGroup.argument('-f', '--format', type=str, choices=['HUMAN', 'JSON'], default='HUMAN')
@BranchCommandGroup.argument('name', type=str)
@BranchCommandGroup.argument('package')
@BranchCommandGroup.command('delete')
def delete_branch(connection, args):
    """Delete branch of repository"""

    console = sap.cli.core.get_console()
    try:
        repo = get_repository(connection, args.package)
        response = repo.delete_branch(args.name)
    except GCTSRequestError as ex:
        dump_gcts_messages(console, ex.messages)
        return 1
    except SAPCliError as ex:
        console.printerr(str(ex))
        return 1

    if args.format.upper() == 'JSON':
        console.printout(sap.cli.core.json_dumps(response))
    else:
        console.printout(f'Branch "{args.name}" was deleted.')

    return 0


def _mark_active_branch(branches, active_branch_name):
    """Mark corresponding local branch as active branch. Remove active branch from list."""

    branches = [branch for branch in branches if branch['type'] != 'active']

    for branch in branches:
        if branch['type'] == 'local' and branch['name'] == active_branch_name:
            branch['name'] += '*'

    return branches


@BranchCommandGroup.argument('-f', '--format', type=str, choices=['HUMAN', 'JSON'], default='HUMAN')
@BranchCommandGroup.argument('-r', '--remote', default=False, action='store_true')
@BranchCommandGroup.argument('-a', '--all', default=False, action='store_true')
@BranchCommandGroup.argument('package')
@BranchCommandGroup.command('list')
def list_branches(connection, args):
    """List branches of repository"""

    console = sap.cli.core.get_console()
    try:
        repo = get_repository(connection, args.package)
        branches = repo.list_branches()
    except GCTSRequestError as ex:
        dump_gcts_messages(console, ex.messages)
        return 1
    except SAPCliError as ex:
        console.printerr(str(ex))
        return 1

    filtered_branches = branches.copy()
    if args.remote:
        filtered_branches = [branch for branch in filtered_branches if branch['type'] == 'remote']
    elif not args.all:
        filtered_branches = [branch for branch in filtered_branches if branch['type'] == 'local']

    if args.format.upper() == 'JSON':
        console.printout(sap.cli.core.json_dumps(filtered_branches))
    else:
        active_branch = next(branch for branch in branches if branch['type'] == 'active')
        filtered_branches = _mark_active_branch(filtered_branches, active_branch['name'])

        columns = (
            sap.cli.helpers.TableWriter.Columns()
            ('name', 'Name')
            ('type', 'Type')
            ('isSymbolic', 'Symbolic')
            ('isPeeled', 'Peeled')
            ('ref', 'Reference')
            .done()
        )
        tw = sap.cli.helpers.TableWriter(filtered_branches, columns)
        tw.printout(console)

    return 0


class RepoCommandGroup(sap.cli.core.CommandGroup):
    """Container for repository commands."""

    def __init__(self):
        super().__init__('repo')

        self.property_grp = PropertyCommandGroup()
        self.branch_grp = BranchCommandGroup()

    def install_parser(self, arg_parser):
        repo_group = super().install_parser(arg_parser)

        property_parser = repo_group.add_parser(self.property_grp.name)
        self.property_grp.install_parser(property_parser)

        branch_parser = repo_group.add_parser(self.branch_grp.name)
        self.branch_grp.install_parser(branch_parser)


@RepoCommandGroup.argument('url')
@RepoCommandGroup.argument('package')
@RepoCommandGroup.command('set-url')
def set_url(connection, args):
    """Set repo URL"""

    warnings.warn(message='Command "set-url" is no longer supported and will be deleted.'
                          ' Use "property set" instead.', category=DeprecationWarning)

    repo = Repository(connection, args.package)

    try:
        repo.set_url(args.url)
    except SAPCliError as ex:
        sap.cli.core.printout(str(ex))
        return 1

    return 0


@RepoCommandGroup.argument('--columns', type=str, default=None, help='Visible columns in CSV')
@RepoCommandGroup.argument('--noheadings', action='store_true', default=False)
@RepoCommandGroup.argument('-f', '--format', type=str, choices=['HUMAN', 'JSON'], default='HUMAN')
@RepoCommandGroup.argument('--operation', type=str, choices=RepoActivitiesQueryParams.allowed_operations(),
                           default=None)
@RepoCommandGroup.argument('--tocommit', type=str, default=None)
@RepoCommandGroup.argument('--fromcommit', type=str, default=None)
@RepoCommandGroup.argument('--offset', type=int, default=0)
@RepoCommandGroup.argument('--limit', type=int, default=10)
@RepoCommandGroup.argument('package')
@RepoCommandGroup.command()
def activities(connection, args):
    """gCTS Activities
    """

    console = sap.cli.core.get_console()

    params = RepoActivitiesQueryParams().set_limit(args.limit).set_offset(args.offset)
    params.set_tocommit(args.tocommit).set_fromcommit(args.fromcommit).set_operation(args.operation)

    try:
        repo = get_repository(connection, args.package)
        repo_activities = repo.activities(params)
    except GCTSRequestError as ex:
        dump_gcts_messages(sap.cli.core.get_console(), ex.messages)
        return 1
    except SAPCliError as ex:
        console.printout(str(ex))
        return 1

    if args.format == 'JSON':
        console.printout(repo_activities)
    else:
        columns = (
            sap.cli.helpers.TableWriter.Columns()
            ('checkoutTime', 'Date', formatter=sap.cli.helpers.abapstamp_to_isodate)
            ('caller', 'Caller')
            ('type', 'Operation')
            ('request', 'Transport', default='')
            ('fromCommit', 'From Commit', default='')
            ('toCommit', 'To Commit', default='')
            ('state', 'State', default='')
            ('rc', 'Code', default='----')
            .done()
        )

        tw = sap.cli.helpers.TableWriter(
            repo_activities,
            columns,
            display_header=not args.noheadings,
            visible_columns=None if not args.columns else args.columns.split(',')
        )
        tw.printout(console)

    return 0


class CommandGroup(sap.cli.core.CommandGroup):
    """Adapter converting command line parameters to sap.rest.gcts
       methods calls.
    """

    def __init__(self):
        super().__init__('gcts')

        self.user_grp = UserCommandGroup()
        self.repo_grp = RepoCommandGroup()

    def install_parser(self, arg_parser):
        gcts_group = super().install_parser(arg_parser)

        user_parser = gcts_group.add_parser(self.user_grp.name)
        self.user_grp.install_parser(user_parser)

        repo_parser = gcts_group.add_parser(self.repo_grp.name)
        self.repo_grp.install_parser(repo_parser)


@CommandGroup.command()
# pylint: disable=unused-argument
def repolist(connection, args):
    """ls"""

    console = sap.cli.core.get_console()

    try:
        response = sap.rest.gcts.simple.fetch_repos(connection)
    except GCTSRequestError as ex:
        dump_gcts_messages(console, ex.messages)
        return 1

    columns = (
        sap.cli.helpers.TableWriter.Columns()
        ('name', 'Name')
        ('branch', 'Branch', default='')
        ('head', 'Commit', default='')
        ('status', 'Status')
        ('vsid', 'vSID')
        ('url', 'URL')
        .done()
    )

    sap.cli.helpers.TableWriter(response, columns).printout(console)

    return 0


@CommandGroup.argument('--heartbeat', type=int, nargs='?', default=0)
@CommandGroup.argument('--vsid', type=str, nargs='?', default='6IT')
@CommandGroup.argument('--starting-folder', type=str, nargs='?', default='src/')
@CommandGroup.argument('--no-fail-exists', default=False, action='store_true')
@CommandGroup.argument('--vcs-token', type=str, nargs='?')
@CommandGroup.argument('-t', '--type', choices=['GITHUB', 'GIT'], default='GITHUB')
@CommandGroup.argument('-r', '--role', choices=['SOURCE', 'TARGET'], default='SOURCE',
                       help='SOURCE=Development, TARGET=Provided')
@CommandGroup.argument('package', nargs='?')
@CommandGroup.argument('url')
@CommandGroup.command()
def clone(connection, args):
    """git clone <repository> [<package>]
    """

    package = args.package
    if not package:
        package = sap.rest.gcts.package_name_from_url(args.url)

    console = sap.cli.core.get_console()

    try:
        with sap.cli.helpers.ConsoleHeartBeat(console, args.heartbeat):
            repo = sap.rest.gcts.simple.clone(connection, args.url, package,
                                              start_dir=args.starting_folder,
                                              vcs_token=args.vcs_token,
                                              vsid=args.vsid,
                                              error_exists=not args.no_fail_exists,
                                              role=args.role,
                                              typ=args.type)
    except GCTSRequestError as ex:
        dump_gcts_messages(sap.cli.core.get_console(), ex.messages)
        return 1

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
        try:
            repo = get_repository(connection, args.package)
            configuration = repo.configuration
        except GCTSRequestError as ex:
            dump_gcts_messages(sap.cli.core.get_console(), ex.messages)
            return 1
        except SAPCliError as ex:
            console.printout(str(ex))
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
        repo = get_repository(connection, args.package)
        sap.rest.gcts.simple.delete(connection, repo=repo)
    except GCTSRequestError as ex:
        dump_gcts_messages(sap.cli.core.get_console(), ex.messages)
        return 1
    except SAPCliError as ex:
        sap.cli.core.printout(str(ex))
        return 1

    sap.cli.core.printout(f'The repository "{repo.name}" has been deleted')
    return 0


@CommandGroup.argument('-f', '--format', choices=['HUMAN', 'JSON'], default='HUMAN')
@CommandGroup.argument('--heartbeat', type=int, nargs='?', default=0)
@CommandGroup.argument('branch')
@CommandGroup.argument('package')
@CommandGroup.command()
def checkout(connection, args):
    """git checkout <branch>
    """

    console = sap.cli.core.get_console()
    try:
        repo = get_repository(connection, args.package)
        old_branch = repo.branch
        with sap.cli.helpers.ConsoleHeartBeat(console, args.heartbeat):
            response = sap.rest.gcts.simple.checkout(connection, args.branch, repo=repo)
    except GCTSRequestError as ex:
        dump_gcts_messages(sap.cli.core.get_console(), ex.messages)
        return 1
    except SAPCliError as ex:
        console.printout(str(ex))
        return 1

    if args.format.upper() == 'JSON':
        console.printout(sap.cli.core.json_dumps(response))
    else:
        console.printout(f'The repository "{repo.name}" has been set to the branch "{args.branch}"')
        console.printout(f'({old_branch}:{response["fromCommit"]}) -> ({args.branch}:{response["toCommit"]})')
    return 0


@CommandGroup.argument('package')
@CommandGroup.command('log')
def gcts_log(connection, args):
    """git log
    """

    console = sap.cli.core.get_console()
    try:
        repo = get_repository(connection, args.package)
        commits = sap.rest.gcts.simple.log(connection, repo=repo)
    except GCTSRequestError as ex:
        dump_gcts_messages(console, ex.messages)
        return 1
    except SAPCliError as ex:
        console.printout(str(ex))
        return 1

    if not commits:
        return 0

    commit_iter = iter(commits)

    commit_item = next(commit_iter)
    print_gcts_commit(console, commit_item)

    for commit_item in commit_iter:
        console.printout('')
        print_gcts_commit(console, commit_item)

    return 0


@CommandGroup.argument('-f', '--format', choices=['HUMAN', 'JSON'], default='HUMAN')
@CommandGroup.argument('--heartbeat', type=int, nargs='?', default=0)
@CommandGroup.argument('package')
@CommandGroup.command()
def pull(connection, args):
    """git pull
    """

    console = sap.cli.core.get_console()

    try:
        repo = get_repository(connection, args.package)
        with sap.cli.helpers.ConsoleHeartBeat(console, args.heartbeat):
            response = sap.rest.gcts.simple.pull(connection, repo=repo)
    except GCTSRequestError as ex:
        dump_gcts_messages(sap.cli.core.get_console(), ex.messages)
        return 1
    except SAPCliError as ex:
        console.printout(str(ex))
        return 1

    if args.format.upper() == 'JSON':
        console.printout(sap.cli.core.json_dumps(response))
    else:
        console.printout(f'The repository "{repo.name}" has been pulled')

        from_commit = response.get('fromCommit')
        to_commit = response.get('toCommit')

        if from_commit is not None:
            console.printout(f'{response["fromCommit"]} -> {response["toCommit"]}')
        elif to_commit is not None:
            console.printout(f'New HEAD is {response["toCommit"]}')

    return 0


@CommandGroup.argument('--heartbeat', type=int, nargs='?', default=0)
@CommandGroup.argument('--description', type=str, default=None)
@CommandGroup.argument('-m', '--message', type=str, default=None)
@CommandGroup.argument('corrnr')
@CommandGroup.argument('package')
@CommandGroup.command()
def commit(connection, args):
    """git commit
    """

    console = sap.cli.core.get_console()

    try:
        repo = get_repository(connection, args.package)
        with sap.cli.helpers.ConsoleHeartBeat(console, args.heartbeat):
            repo.commit_transport(args.corrnr, args.message or f'Transport {args.corrnr}', args.description)
    except GCTSRequestError as ex:
        dump_gcts_messages(sap.cli.core.get_console(), ex.messages)
        return 1
    except SAPCliError as ex:
        console.printout(str(ex))
        return 1

    console.printout(f'The transport "{args.corrnr}" has been committed')
    return 0
