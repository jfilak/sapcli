"""gCTS methods"""

import os
import warnings

import sap.cli.core
import sap.cli.helpers
import sap.rest.gcts.simple
from sap.rest.gcts.simple import (
    get_task_timeout_error_message,
)
from sap.rest.gcts.sugar import (
    abap_modifications_disabled,
    SugarOperationProgress,
    temporary_switched_branch
)
from sap.rest.gcts.remote_repo import (
    Repository,
    RepoActivitiesQueryParams,
)
from sap.rest.gcts.repo_task import (
    RepositoryTask,
)
from sap.rest.gcts.errors import (
    GCTSRequestError,
    GCTSRepoAlreadyExistsError,
    SAPCliError,
)
from sap.rest.errors import HTTPRequestError
from sap.cli.gcts_task import CommandGroup as TaskCommandGroup
from sap.cli.gcts_utils import gcts_exception_handler

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

        repo = repositories[0]
        repo.wipe_data()
        return repo

    return Repository(connection, package)


def get_activity_rc(repo, operation: RepoActivitiesQueryParams.Operation):
    """Get the return code of the operation"""

    activities_params = RepoActivitiesQueryParams().set_operation(operation.value)
    try:
        activities_list = repo.activities(activities_params)
    except HTTPRequestError as exc:
        raise SAPCliError(f'Unable to obtain activities of repository: "{repo.rid}"\n{exc}') from exc

    if not activities_list:
        raise SAPCliError(f'Expected {operation.value} activity not found! Repository: "{repo.rid}"')

    return int(activities_list[0]['rc'])


class UserCommandGroup(sap.cli.core.CommandGroup):
    """Container for user commands."""
    commands_wrapper = gcts_exception_handler

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
    commands_wrapper = gcts_exception_handler

    def __init__(self):
        super().__init__('property')


@PropertyCommandGroup.argument('property', nargs="?", default=None)
@PropertyCommandGroup.argument('package')
@PropertyCommandGroup.command('get')
def get_properties(connection, args):
    """Get all repository properties"""

    properties = [
        ('Name', 'name'),
        ('RID', 'rid'),
        ('Branch', 'branch'),
        ('Commit', 'head'),
        ('Status', 'status'),
        ('vSID', 'vsid'),
        ('Role', 'role'),
        ('URL', 'url'),
    ]

    console = sap.cli.core.get_console()
    repo = get_repository(connection, args.package)

    if args.property:
        try:
            prop = next(iter((prop for prop in properties if prop[0] == args.property)))
        except StopIteration:
            console.printerr('The property was not found:', args.property)
            return 1

        console.printout(getattr(repo, prop[1]))
    else:
        for prop in properties:
            console.printout(f'{prop[0]}: {getattr(repo, prop[1])}')

    return 0


@PropertyCommandGroup.argument('value')
@PropertyCommandGroup.argument('property_name')
@PropertyCommandGroup.argument('package')
@PropertyCommandGroup.command('set')
def set_properties(connection, args):
    """Set the property of repository"""

    repo = get_repository(connection, args.package)
    repo.set_item(args.property_name.lower(), args.value)

    return 0


class BranchCommandGroup(sap.cli.core.CommandGroup):
    """Container for branch commands"""
    commands_wrapper = gcts_exception_handler

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
    repo = get_repository(connection, args.package)
    response = repo.create_branch(args.name, symbolic=args.symbolic, peeled=args.peeled, local_only=args.local_only)

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
    repo = get_repository(connection, args.package)
    response = repo.delete_branch(args.name)

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
    repo = get_repository(connection, args.package)
    branches = repo.list_branches()

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
    commands_wrapper = gcts_exception_handler

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
    repo.set_url(args.url)

    return 0


@RepoCommandGroup.argument('package')
@RepoCommandGroup.command('set-role-target')
def set_role_target(connection, args):
    """Set repo Role to TARGET"""

    repo = get_repository(connection, args.package)
    repo.set_role('TARGET')

    return 0


@RepoCommandGroup.argument('package')
@RepoCommandGroup.command('set-role-source')
def set_role_source(connection, args):
    """Set repo Role to SOURCE"""

    repo = get_repository(connection, args.package)
    repo.set_role('SOURCE')

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

    repo = get_repository(connection, args.package)
    repo_activities = repo.activities(params)

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


class ConfigCommandGroup(sap.cli.core.CommandGroup):
    """Container for config commands."""
    commands_wrapper = gcts_exception_handler

    def __init__(self):
        super().__init__('config')


def _print_config_property(console, config_property, output_format):
    """Print system configuration property"""

    if output_format == 'JSON':
        console.printout(sap.cli.core.json_dumps(config_property))
    else:
        console.printout(f'Key: {config_property["key"]}')
        console.printout(f'Value: {config_property["value"]}')


@ConfigCommandGroup.argument('-f', '--format', type=str, choices=['HUMAN', 'JSON'], default='HUMAN')
@ConfigCommandGroup.argument('key', type=str)
@ConfigCommandGroup.command('get')
def get_system_config_property(connection, args):
    """Get configuration property value for given key"""

    console = sap.cli.core.get_console()
    config_property = sap.rest.gcts.simple.get_system_config_property(connection, args.key.upper())

    _print_config_property(console, config_property, args.format.upper())

    return 0


@ConfigCommandGroup.argument('-f', '--format', type=str, choices=['HUMAN', 'JSON'], default='HUMAN')
@ConfigCommandGroup.command('list')
def list_system_config(connection, args):
    """List system configuration"""
    console = sap.cli.core.get_console()
    config_list = sap.rest.gcts.simple.list_system_config(connection)

    if args.format.upper() == 'JSON':
        console.printout(sap.cli.core.json_dumps(config_list))
    else:
        columns = (
            sap.cli.helpers.TableWriter.Columns()
            ('key', 'Key')
            ('value', 'Value')
            ('category', 'Category')
            ('changedAt', 'Changed At')
            ('changedBy', 'Changed By')
            .done()
        )

        tw = sap.cli.helpers.TableWriter(config_list, columns)
        tw.printout(console)

    return 0


@ConfigCommandGroup.argument('-f', '--format', type=str, choices=['HUMAN', 'JSON'], default='HUMAN')
@ConfigCommandGroup.argument('value', type=str)
@ConfigCommandGroup.argument('key', type=str)
@ConfigCommandGroup.command('set')
def set_system_config_property(connection, args):
    """Create or update the configuration property"""

    console = sap.cli.core.get_console()
    config_property = sap.rest.gcts.simple.set_system_config_property(connection, args.key.upper(), args.value)

    _print_config_property(console, config_property, args.format.upper())

    return 0


@ConfigCommandGroup.argument('-f', '--format', type=str, choices=['HUMAN', 'JSON'], default='HUMAN')
@ConfigCommandGroup.argument('key', type=str)
@ConfigCommandGroup.command('unset')
def delete_system_config_property(connection, args):
    """Delete configuration property"""

    console = sap.cli.core.get_console()
    response = sap.rest.gcts.simple.delete_system_config_property(connection, args.key.upper())

    if args.format.upper() == 'JSON':
        console.printout(sap.cli.core.json_dumps(response))
    else:
        console.printout(f'Config property "{args.key.upper()}" was unset.')

    return 0


class SystemCommandGroup(sap.cli.core.CommandGroup):
    """Container for system commands."""

    def __init__(self):
        super().__init__('system')

        self.config_grp = ConfigCommandGroup()

    def install_parser(self, arg_parser):
        system_group = super().install_parser(arg_parser)

        config_parser = system_group.add_parser(self.config_grp.name)
        self.config_grp.install_parser(config_parser)


class CommandGroup(sap.cli.core.CommandGroup):
    """Adapter converting command line parameters to sap.rest.gcts
       methods calls.
    """
    commands_wrapper = gcts_exception_handler

    def __init__(self):
        super().__init__('gcts')

        self.user_grp = UserCommandGroup()
        self.repo_grp = RepoCommandGroup()
        self.system_grp = SystemCommandGroup()
        self.task_grp = TaskCommandGroup()

    def install_parser(self, arg_parser):
        gcts_group = super().install_parser(arg_parser)

        user_parser = gcts_group.add_parser(self.user_grp.name)
        self.user_grp.install_parser(user_parser)

        repo_parser = gcts_group.add_parser(self.repo_grp.name)
        self.repo_grp.install_parser(repo_parser)

        system_parser = gcts_group.add_parser(self.system_grp.name)
        self.system_grp.install_parser(system_parser)

        task_parser = gcts_group.add_parser('task')
        self.task_grp.install_parser(task_parser)


@CommandGroup.command()
# pylint: disable=unused-argument
def repolist(connection, args):
    """ls"""

    console = sap.cli.core.get_console()

    response = sap.rest.gcts.simple.fetch_repos(connection)

    columns = (
        sap.cli.helpers.TableWriter.Columns()
        ('name', 'Name')
        ('rid', 'RID')
        ('branch', 'Branch', default='')
        ('head', 'Commit', default='')
        ('status', 'Status')
        ('vsid', 'vSID')
        ('url', 'URL')
        .done()
    )

    sap.cli.helpers.TableWriter(response, columns).printout(console)

    return 0


@CommandGroup.argument('--wait-for-ready', type=int, nargs='?', default=0)
@CommandGroup.argument('--heartbeat', type=int, nargs='?', default=0)
@CommandGroup.argument('--vsid', type=str, nargs='?', default='6IT')
@CommandGroup.argument('--starting-folder', type=str, nargs='?', default='src/')
@CommandGroup.argument('--no-fail-exists', default=False, action='store_true')
@CommandGroup.argument('--sync-clone', default=False, action='store_true')
@CommandGroup.argument('--pull-period', type=int, nargs='?', default=30, help='Period in seconds to pull the repository  clone task status')
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
        repo = sap.rest.gcts.simple.create(connection, args.url, package,
                                           start_dir=args.starting_folder,
                                           vcs_token=args.vcs_token,
                                           vsid=args.vsid,
                                           error_exists=not args.no_fail_exists,
                                           role=args.role,
                                           typ=args.type)
    except GCTSRepoAlreadyExistsError as exc:
        console.printout('Repository already exists.')
        console.printerr(str(exc))
        return 1
    except GCTSRequestError as exc:
        console.printout('Repository creation request responded with an error.')
        console.printerr(str(exc))
        return 1

    if getattr(args, 'sync_clone', False):
        try:
            with sap.cli.helpers.ConsoleHeartBeat(console, args.heartbeat):
                sap.rest.gcts.simple.clone(repo)
        except HTTPRequestError as exc:
            if args.wait_for_ready > 0:
                repo = get_repository(connection, args.url)

                console.printout('Clone request responded with an error. Checking clone process ...')
                clone_rc = get_activity_rc(repo, RepoActivitiesQueryParams.Operation.CLONE)
                if clone_rc != Repository.ActivityReturnCode.CLONE_SUCCESS.value:
                    console.printerr(f'Clone process failed with return code: {clone_rc}!')
                    console.printerr(str(exc))
                    return 1

                console.printout('Clone process finished successfully. Waiting for repository to be ready ...')
                with sap.cli.helpers.ConsoleHeartBeat(console, args.heartbeat):
                    def is_clone_done(repo: Repository):
                        return repo.is_cloned

                    sap.rest.gcts.simple.wait_for_operation(repo, is_clone_done, args.wait_for_ready, exc)

            else:
                console.printout('Clone request responded with an error. Checkout "--wait-for-ready" parameter!')
                console.printerr(str(exc))
                return 1
    else:
        try:
            task = sap.rest.gcts.simple.schedule_clone(repo, connection)

            if isinstance(task, RepositoryTask) and task.tid:
                if args.wait_for_ready > 0:
                    with sap.cli.helpers.ConsoleHeartBeat(console, args.heartbeat):
                        sap.rest.gcts.simple.wait_for_task_execution(
                            task, args.wait_for_ready,
                            args.pull_period, sap.cli.helpers.print_gcts_task_info)
                else:
                    console.printout(get_task_timeout_error_message(task))
                    return 0
            else:
                console.printout('Clone request responded with an error. No task found!')
                return 1

            # update data after cloning
            repo = get_repository(connection, args.url)

        except HTTPRequestError as exc:
            console.printout('Clone request responded with an error.')
            console.printerr(str(exc))
            return 1

    console.printout('Cloned repository:')
    console.printout(' URL   :', repo.url)
    console.printout(' branch:', repo.branch)
    console.printout(' HEAD  :', repo.head)

    return 0


@CommandGroup.argument('value', nargs='?', default=None)
@CommandGroup.argument('name', nargs='?', default=None)
@CommandGroup.argument('package')
@CommandGroup.argument('--unset', default=False, action='store_true')
@CommandGroup.argument('-l', '--list', default=False, action='store_true')
@CommandGroup.command()
def config(connection, args):
    """git config [-l] [<package>]
    """

    def _list():
        """List configuration"""

        configuration = repo.configuration

        for key, value in configuration.items():
            console.printout(f'{key}={value}')

    def _set():
        """Set configuration value"""

        old_value = repo.get_config(args.name) or ''
        if args.value is None:
            raise SAPCliError('Cannot execute the set operation: "VALUE" was not provided.')

        repo.set_config(args.name, args.value)
        console.printout(f'{args.name}={old_value} -> {args.value}')

    def _unset():
        """Unset configuration value"""

        old_value = repo.get_config(args.name) or ''
        repo.delete_config(args.name)
        console.printout(f'unset {args.name}={old_value}')

    console = sap.cli.core.get_console()
    if args.package is None or not args.list and args.name is None:
        console.printerr('Invalid command line options\nRun: sapcli gcts config --help')
        return 1

    repo = get_repository(connection, args.package)

    if args.list:
        _list()
    elif args.unset:
        _unset()
    else:
        _set()

    return 0


@CommandGroup.argument('package')
@CommandGroup.command()
def delete(connection, args):
    """rm
    """

    repo = get_repository(connection, args.package)
    sap.rest.gcts.simple.delete(connection, repo=repo)

    sap.cli.core.printout(f'The repository "{repo.rid}" has been deleted')
    return 0


@CommandGroup.argument('-f', '--format', choices=['HUMAN', 'JSON'], default='HUMAN')
@CommandGroup.argument('--wait-for-ready', type=int, nargs='?', default=0)
@CommandGroup.argument('--heartbeat', type=int, nargs='?', default=0)
@CommandGroup.argument('branch')
@CommandGroup.argument('package')
@CommandGroup.command()
def checkout(connection, args):
    """git checkout <branch>
    """

    console = sap.cli.core.get_console()
    repo = get_repository(connection, args.package)
    old_branch = repo.branch
    from_commit = repo.head
    try:
        with sap.cli.helpers.ConsoleHeartBeat(console, args.heartbeat):
            response = sap.rest.gcts.simple.checkout(connection, args.branch, repo=repo)

    except HTTPRequestError as exc:
        if args.wait_for_ready > 0:
            repo = get_repository(connection, args.package)

            console.printout('Checkout request responded with an error. Checking checkout process ...')
            checkout_rc = get_activity_rc(repo, RepoActivitiesQueryParams.Operation.BRANCH_SW)
            if checkout_rc != Repository.ActivityReturnCode.BRANCH_SW_SUCCES.value:
                console.printerr(f'Checkout process failed with return code: {checkout_rc}!')
                console.printerr(str(exc))
                return 1

            console.printout('Checkout process finished successfully. Waiting for repository to be ready ...')
            with sap.cli.helpers.ConsoleHeartBeat(console, args.heartbeat):
                def is_checkout_done(repo: Repository):
                    return repo.branch == args.branch

                sap.rest.gcts.simple.wait_for_operation(repo, is_checkout_done, args.wait_for_ready, exc)

        else:
            console.printout('Checkout request responded with an error. Checkout "--wait-for-ready" parameter!')
            console.printerr(str(exc))
            return 1
    else:
        repo.wipe_data()

    to_commit = repo.head
    if args.format.upper() == 'JSON':
        console.printout(sap.cli.core.json_dumps(response))
    else:
        console.printout(f'The repository "{repo.rid}" has been set to the branch "{args.branch}"')
        console.printout(f'({old_branch}:{from_commit}) -> ({args.branch}:{to_commit})')
    return 0


@CommandGroup.argument('package')
@CommandGroup.command('log')
def gcts_log(connection, args):
    """git log
    """

    console = sap.cli.core.get_console()
    repo = get_repository(connection, args.package)
    commits = sap.rest.gcts.simple.log(connection, repo=repo)

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

    repo = get_repository(connection, args.package)
    with sap.cli.helpers.ConsoleHeartBeat(console, args.heartbeat):
        response = sap.rest.gcts.simple.pull(connection, repo=repo)

    if args.format.upper() == 'JSON':
        console.printout(sap.cli.core.json_dumps(response))
    else:
        console.printout(f'The repository "{repo.rid}" has been pulled')

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
@CommandGroup.argument('-d', '--devc', type=str, default=None,
                       help="Name of committed ABAP package if corrnr is not give. "
                            "Default: the repository name aka the parameter package")
@CommandGroup.argument('corrnr', type=str, nargs='?', default=None)
@CommandGroup.argument('package')
@CommandGroup.command()
def commit(connection, args):
    """git commit
    """

    console = sap.cli.core.get_console()

    repo = get_repository(connection, args.package)
    if args.corrnr is None:
        devc = args.devc or args.package
        devc = devc.upper()
        with sap.cli.helpers.ConsoleHeartBeat(console, args.heartbeat):
            repo.commit_package(devc, args.message or f'Export package {devc}', args.description)
        console.printout(f'The package "{devc}" has been committed')
    else:
        with sap.cli.helpers.ConsoleHeartBeat(console, args.heartbeat):
            repo.commit_transport(args.corrnr, args.message or f'Transport {args.corrnr}', args.description)
        console.printout(f'The transport "{args.corrnr}" has been committed')

    return 0


class ConsoleSugarOperationProgress(SugarOperationProgress):
    """Handler for progress message of sugar operations"""

    def __init__(self, console):
        super().__init__()
        self._console = console

    def _handle_updated(self, message, recover_message):
        self._console.printout(message)


@BranchCommandGroup.argument('-o', '--output', default=None,
                             help='Write response in the required format to the given file')
@BranchCommandGroup.argument('branch')
@BranchCommandGroup.argument('package')
@BranchCommandGroup.command()
def update_filesystem(connection, args):
    """Update branch on filesystem only
    """
    console = sap.cli.core.get_console()

    if args.output and os.path.exists(args.output):
        console.printerr(f'Output file must not exist: {args.output}')
        return 1

    repo = get_repository(connection, args.package)
    checkout_progress = ConsoleSugarOperationProgress(console)
    noimports_progress = ConsoleSugarOperationProgress(console)
    pull_response = None
    errored = True
    try:
        with abap_modifications_disabled(repo, progress=noimports_progress):
            with temporary_switched_branch(repo, args.branch, progress=checkout_progress):
                console.printout(f'Updating the currently active branch {args.branch} ...')
                pull_response = repo.pull()
                from_commit = pull_response.get('fromCommit') or '()'
                to_commit = pull_response.get('toCommit') or '()'
                console.printout(f'The branch "{args.branch}" has been updated: {from_commit} -> {to_commit}')
    except GCTSRequestError as ex:
        dump_gcts_messages(sap.cli.core.get_console(), ex.messages)
    except SAPCliError as ex:
        console.printerr(str(ex))
    else:
        errored = False

    if pull_response and args.output:
        console.printout(f'Writing gCTS JSON response to {args.output} ...')
        with open(args.output, 'x', encoding='utf-8') as output_file:
            output_file.write(sap.cli.core.json_dumps(pull_response))
        console.printout(f'Successfully wrote gCTS JSON response to {args.output}')

    if errored:
        if checkout_progress.recover_message:
            console.printerr(checkout_progress.recover_message)
        if noimports_progress.recover_message:
            console.printerr(noimports_progress.recover_message)
        return 1

    return 0
