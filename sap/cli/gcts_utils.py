"""gCTS CLI utilities"""
import sap.cli.core
from sap.rest.gcts.errors import GCTSRequestError, SAPCliError
from sap.rest.gcts.remote_repo import RepoActivitiesQueryParams
from sap.rest.errors import HTTPRequestError


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


def print_gcts_task_info(err_msg: str | None = None, task: dict | None = None):
    """Print out the task information"""
    console = sap.cli.core.get_console()
    if err_msg:
        console.printerr(err_msg)
    elif task:
        console.printout(f'\nTask Status: {task["status"]}')
