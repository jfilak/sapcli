"""gCTS CLI utilities"""
from typing import List

import sap.cli.core
from sap.cli.core import PrintConsole
import sap.cli.helpers

from sap.rest.gcts.errors import GCTSRequestError, GCTSProcessError, SAPCliError
from sap.rest.gcts.sugar import LogTaskOperationProgress, SugarOperationProgress
from sap.rest.gcts.log_messages import ProcessMessage


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


def print_process_message_details(console, message: ProcessMessage) -> None:
    """Print details of a process message (applInfo content)"""

    console.printout(message.appl_info.formatted_str(indent=4))


def print_process_messages(console, messages: List[ProcessMessage]) -> None:
    """Print gCTS list of ProcessMessage in a table format"""

    columns = (
        sap.cli.helpers.TableWriter.Columns()
        ('time', 'Date', formatter=sap.cli.helpers.abapstamp_to_isodate)
        ('action', 'Action')
        ('application', 'Application')
        ('severity', 'Severity')
        .done()
    )

    tw = sap.cli.helpers.TableWriter(messages, columns)
    tw.printout(console, line_callback=print_process_message_details)


def gcts_exception_handler(func):
    """Exception handler for gcts commands
       This decorator should be used only on sap/cli/ command handler functions
       because we expect it being called with 2 arguments: connection, args.
       Especially the args is important because we use it to get 'console_factory'.
    """
    def _handler(connection, args):
        console_factory = sap.cli.core.get_console
        if hasattr(args, 'console_factory'):
            console_factory = args.console_factory
        try:
            return func(connection, args)
        except GCTSRequestError as ex:
            dump_gcts_messages(console_factory(), ex.messages)
            return 1
        except GCTSProcessError as ex:
            print_process_messages(console_factory(), ex.process_messages)
            return 1
        except SAPCliError as ex:
            console_factory().printerr(str(ex))
            return 1
    return _handler


def print_gcts_task_info(console, err_msg: str | None = None, task: dict | None = None):
    """Print out the task information"""
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
        print_gcts_task_info(self._console, error_msg, task)

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


DEFAULT_PGMID = 'R3TR'


def parse_object_spec(spec: str) -> List[tuple]:
    """Parses the command line object specification [PGMID:]TYPE:NAME[,NAME...]
       and returns the list of upper cased triples (PGMID, TYPE, NAME).
    """

    parts = [part.strip() for part in spec.upper().split(':')]
    if len(parts) == 2:
        parts.insert(0, DEFAULT_PGMID)

    if len(parts) != 3:
        raise SAPCliError(f'Invalid object "{spec}": expected [PGMID:]TYPE:NAME[,NAME...]')

    pgmid, objtype, name_list = parts
    names = [name.strip() for name in name_list.split(',')]
    if not pgmid or not objtype or not all(names):
        raise SAPCliError(f'Invalid object "{spec}": expected [PGMID:]TYPE:NAME[,NAME...]')

    if any('\r' in name or '\n' in name for name in names):
        raise SAPCliError(f'Invalid object "{spec}": names must not contain line breaks')

    return [(pgmid, objtype, name) for name in names]


def parse_object_list(lines, source: str) -> List[tuple]:
    """Parses the transport object list - the lines PGMID TYPE NAME where NAME
       is the rest of the line because it may contain spaces - and returns
       the list of triples (PGMID, TYPE, NAME). NAME is kept as is because
       some object names are case sensitive (e.g. BSP pages). Empty lines and
       lines starting with # are skipped. The parameter source is used in
       error messages.
    """

    objects = []
    for lineno, line in enumerate(lines, start=1):
        line = line.strip()
        if not line or line.startswith('#'):
            continue

        parts = line.split(None, 2)
        if len(parts) != 3:
            raise SAPCliError(f'{source}:{lineno}: Invalid object "{line}": expected PGMID TYPE NAME')

        pgmid, objtype, name = parts
        objects.append((pgmid.upper(), objtype.upper(), name))

    return objects
