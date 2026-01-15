"""gCTS CLI utilities"""
import sap.cli.core
from sap.cli.core import PrintConsole

from sap.rest.gcts.errors import GCTSRequestError, SAPCliError
from sap.rest.gcts.sugar import LogTaskOperationProgress, SugarOperationProgress


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


def print_process_message_details(console, message):
    """Print details of a process message (applInfo content)"""

    console.printout(message.appl_info.formatted_str(indent=4))


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


def print_gcts_task_info(err_msg: str | None = None, task: dict | None = None):
    """Print out the task information"""
    console = sap.cli.core.get_console()
    if err_msg:
        console.printerr(err_msg)
    elif task:
        console.printout(f'\nTask Status: {task["status"]}')


def gcts_activity_rc_handler(console, activity_name, rc):
    """Simple handler printing information about activity result code to console
    Use it with the functools.partial to create specific handlers for different activities.
    Args:
        console (PrintConsole): Console to print messages to (bind it int partial)
        activity_name (str): Name of the activity (bind it in partial; e.g. Clone, Checkout)
        rc (int): Return code of the activity (this will be provided by the caller - do not bind)
    """

    console.printout(f'{activity_name} activity finished with return code: {rc}')


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
