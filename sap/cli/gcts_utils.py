"""gCTS CLI utilities"""
import sap.cli.core
from sap.rest.gcts.errors import GCTSRequestError, SAPCliError
from sap.rest.gcts.remote_repo import Repository, RepoActivitiesQueryParams
from sap.rest.errors import HTTPRequestError
from sap.rest.gcts.sugar import LogTaskOperationProgress, SugarOperationProgress
from sap.cli.core import PrintConsole


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


def get_activity_rc(repo, operation: RepoActivitiesQueryParams.Operation):
    """Get the return code of the operation"""

    activities_params = RepoActivitiesQueryParams().set_operation(operation.value)
    try:
        activities_list = repo.activities(activities_params)
    except HTTPRequestError as exc:
        raise SAPCliError(f'Unable to obtain activities of repository: "{repo.rid}"\n{exc}') from exc

    if not activities_list or activities_list[0]['rc'] is None:
        raise SAPCliError(f'Expected {operation.value} activity not found! Repository: "{repo.rid}"')

    return int(activities_list[0]['rc'])


def is_clone_activity_success(console, repo: Repository) -> bool:
    """Check if the cloned activity is successful"""
    clone_rc = get_activity_rc(repo, RepoActivitiesQueryParams.Operation.CLONE)
    if clone_rc > Repository.ActivityReturnCode.CLONE_SUCCESS.value:
        console.printerr(f'Clone process failed with return code: {clone_rc}!')
        return False
    return True


def is_checkout_activity_success(console, repo: Repository) -> bool:
    """Check if the checkout activity is successful"""
    checkout_rc = get_activity_rc(repo, RepoActivitiesQueryParams.Operation.BRANCH_SW)
    if checkout_rc > Repository.ActivityReturnCode.BRANCH_SW_SUCCES.value:
        console.printerr(f'Checkout process failed with return code: {checkout_rc}!')
        return False
    return True


def print_gcts_task_info(err_msg: str | None = None, task: dict | None = None):
    """Print out the task information"""
    console = sap.cli.core.get_console()
    if err_msg:
        console.printerr(err_msg)
    elif task:
        console.printout(f'\nTask Status: {task["status"]}')


class TaskOperationProgress(LogTaskOperationProgress):
    """Progress of task operations"""

    def __init__(self, console: PrintConsole):
        super().__init__()
        self._console = console

    # for printing task info to console
    def update_task(self, error_msg: str | None, task: dict | None):
        print_gcts_task_info(error_msg, task)

    # for context logging
    def _handle_updated(self, message, recover_message, pid):
        self._console.printout(message)

    def _handle_recover(self, message):
        self._console.printerr(message)

    # for task progress logging
    def progress_message(self, message: str):
        self._console.printout(message)

    def progress_error(self, message: str):
        self._console.printerr(message)


class ConsoleSugarOperationProgress(SugarOperationProgress):
    """Handler for progress message of sugar operations"""

    def __init__(self, console):
        super().__init__()
        self._console = console

    def _handle_updated(self, message, recover_message, pid):
        self._console.printout(message)

    def _handle_recover(self, message):
        self._console.printerr(message)
