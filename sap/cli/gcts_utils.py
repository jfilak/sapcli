"""gCTS CLI utilities"""

import sap.cli.core
from sap.rest.gcts.errors import GCTSRequestError, SAPCliError
from sap.rest.gcts.remote_repo import Repository
from sap.rest.gcts.remote_repo import RepoActivitiesQueryParams
from sap.rest.errors import HTTPRequestError


def get_activity_rc(repo: Repository, operation: RepoActivitiesQueryParams.Operation):
    """Get the return code of the operation"""

    activities_params = RepoActivitiesQueryParams().set_operation(operation.value)
    try:
        activities_list = repo.activities(activities_params)
   
    except HTTPRequestError as exc:
        raise SAPCliError(f'Unable to obtain activities of repository: "{repo.rid}"\n{exc}') from exc

    if not activities_list:
        raise SAPCliError(f'Expected {operation.value} activity not found! Repository: "{repo.rid}"')

    return int(activities_list[0]['rc'])


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


def gcts_exception_handler(func):
    """Exception handler for gcts commands"""
    def _handler(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except GCTSRequestError as ex:
            dump_gcts_messages(sap.cli.core.get_console(), ex.messages)
            return 1
        except SAPCliError as ex:
            sap.cli.core.get_console().printerr(str(ex))
            return 1
    return _handler


def is_repo_cloned(console, repo: Repository):
    """Check if the repository is cloned"""

    is_buffer_only = repo.get_config('VCS_BUFFER_ONLY') == 'X'
    is_import_disabled = repo.get_config('VCS_NO_IMPORT') == 'X'
    if is_buffer_only or is_import_disabled:
        # check only status of the repository
        if repo.status != 'READY':
            console.printerr(f'Clone process failed. Repository status: {repo.status}')
            return False
        return True
    # check if the repository activities
    clone_rc = get_activity_rc(repo, RepoActivitiesQueryParams.Operation.CLONE)
    if clone_rc != Repository.ActivityReturnCode.CLONE_SUCCESS.value:
        console.printerr(f'Clone process failed with return code: {clone_rc}!')
        return False
    return True


def is_checkout_done(console, repo: Repository, expected_branch: str):
    """Check if the repository is cloned"""

    is_buffer_only = repo.get_config('VCS_BUFFER_ONLY') == 'X'
    is_import_disabled = repo.get_config('VCS_NO_IMPORT') == 'X'
    if is_buffer_only or is_import_disabled:
        # check only expected branch
        if repo.branch != expected_branch:
            console.printerr(f'Checkout process failed. Repository branch: {repo.branch} is not expected: {expected_branch}')
            return False
        return True
    # check if the repository activities
    checkout_rc = get_activity_rc(repo, RepoActivitiesQueryParams.Operation.BRANCH_SW)
    if checkout_rc != Repository.ActivityReturnCode.BRANCH_SW_SUCCES.value:
        console.printerr(f'Checkout process failed with return code: {checkout_rc}!')
        return False
    return True
