#!/usr/bin/env python3

import sys
import time

import sap.rfc.stc as stc
from sap.rfc.types import TRUE, FALSE


def _print_session_current_task_logs(console, conn, session_id, task):
    logs = stc.tm_session_get_log(conn, session_id)
    task_logs = logs.get_task_messages(task['TASKNAME'], task['LNR'])

    for log in task_logs:
        typ = log['TYPE']
        if typ in ['W', 'E', 'A']:
            console.printout('Task log:', log['TYPE'], log['MESSAGE'])


def _do_skip_task(console, conn, session_id, task, lnr):
    console.printout('Skipping: {}:{}'.format(task, lnr))
    ret = stc.tm_task_skip(conn, session_id, task, lnr)

    if not ret['E_SKIPPED']:
        console.printout(ret['ET_RETURN'][0]['MESSAGE'])
        return False

    return True


def _task_execute_wrapper(conn, args):
    if hasattr(args, 'id') and args.TASK_ID:
        task_id = args.id.split(':')
        args.name = task_id[0]

        if len(task_id) == 1:
            args.lnr = None
        elif len(task_id) ==2:
            args.lnr = int(task_id[1])
        else:
            raise ValueError('Invalid format of Task ID (TASK_NAME:LNR): {}'.format(ARGS.TASK_ID))

    args.execute_impl(conn, args)


class TaskGroup(sap.cli.core.CommandGroup):
    """Container for Tasks."""

    def __init__(self):
        super().__init__('task')

    def decorate_command_parser(self, parser, command):
        parser.set_defaults(execute=_task_execute_wrapper, execute_impl=command.handler)
        parser.add_argument('SESSION_ID', dest='session_id', type=str, help='Session ID of the Task')
        parser.add_argument('-n', '--name', dest='task_name', type=str, help='Task Name')
        parser.add_argument('-l', '--lnr', dest='task_lnr', type=str, help='Task Line Number')
        parser.add_argument('-i', '--id', dest='task_id', type=str, help='"Task Name":"Task Line Number"')


class SessionGroup(sap.cli.core.CommandGroup):
    """Container for Sessions."""

    def __init__(self):
        super().__init__('session')

        self.task_grp = TaskGroup()

    def install_parser(self, arg_parser):
        session_group = super().install_parser(arg_parser)

        task_parser = session_group.add_parser(self.task_grp.name)

        self.task_grp.install_parser(task_parser)


class CommandGroup(sap.cli.core.CommandGroup):
    """Adapter converting command line parameters to sap.rfc.stc
       methods calls.
    """

    def __init__(self):
        super().__init__('stc')

        self.sessoin_grp = SessionGroup()

    def install_parser(self, arg_parser):
        stc_group = super().install_parser(arg_parser)

        session_parser = stc_group.add_parser(self.session_grp.name)

        self.session_grp.install_parser(session_parser)


@SessionGroup.command('list')
def session_list(connection, args):
    """List of task list runs"""

    console = sap.cli.core.get_console()
    for session in stc.tm_get_session_list(conn):
        console.printout(session['SESSION_ID'])

    return 0


@SessionGroup.argument('SCENARIO', type=str,
                       help='Task List Name')
@SessionGroup.argument('-s', '--start', default=False, action='store_true',
                       help='Start the execution after creating')
@SessionGroup.argument('-p', '--parameter', action='append', type=str,
                       help='A comma separated tuple "task name,line nr,field name,value" for initial scoping')
@SessionGroup.command('begin')
def session_begin(connection, args):
    """Create a new session from SCENARIO"""

    console = sap.cli.core.get_console()
    session_parameters = list()

    if args.parameter:
        session_parameters = stc.parse_session_parameter_str_list(args.parameter)

    do_not_run = FALSE if args.start else TRUE
    res = stc.tm_session_begin(conn, args.SCENARIO, parameters=session_parameters, init_only=do_not_run)
    console.printout(res['E_SESSION_ID'])

    return 0


@SessionGroup.argument('SESSION_ID', type=str, help='Session ID')
@SessionGroup.argument('-t', '--tasks', action='store_true', default=False,
                       help='Include also task statuses')
@SessionGroup.command('status')
def session_status(connection, args):
    """Get Session status"""

    console = sap.cli.core.get_console()

    status = stc.tm_session_get_status(conn, args.SESSION_ID)
    console.printout('Status:', status['E_STATUS'])

    if args.tasks:
        console.printout('Tasks:')
        for task in status['ET_TASKLIST']:
            console.printout('  - [' + task['CHECK_STATUS'] + '] ' + task['TASKNAME'] + ':' + str(task['LNR']))

    return 0


def _do_session_resume(conn, session_id):
    stc.tm_session_resume(conn, session_id)


@SessionGroup.argument('SESSION_ID', type=str, help='Session ID')
@SessionGroup.command('resume')
def session_resume(connection, args):
    """Continue/Start processing the session"""

    _do_session_resume(conn, args.SESSION_ID)

    return 0


@SessionGroup.argument('-s', '--skip-tasks', action='store_true', default=False, help='skip task and continue')
@SessionGroup.argument('SESSION_ID', type=str, help='Session ID')
@SessionGroup.command('wait')
def session_wait(connection, args):
    """Waits until processing"""

    console = sap.cli.core.get_console()

    while True:
        status = stc.tm_session_get_status(conn, args.SESSION_ID)
        status_code = status['E_STATUS']

        console.printout('Session Status:', status_code, status['E_STATUS_DESCR'])

        if status_code == stc.STC_SESSION_STATUS.NO_NEED_TO_BE_EXECUTED:
            console.printout('Notneeded SessionID:', args.SESSION_ID)
            sys.exit(0)

        if status_code in [stc.STC_SESSION_STATUS.FINISHED_SUCCESSFULLY, stc.STC_SESSION_STATUS.FINISHED_WITH_WARNINGS]:
            console.printout('Finished SessionID:', args.SESSION_ID)
            sys.exit(0)

        task = status['ES_CURRENT_TASK']
        task_status_code = task['STATUS']

        console.printout('Current Task Status:', task_status_code, task['STATUS_DESCR'], '-', task['DESCRIPTION'])

        if status_code == stc.STC_SESSION_STATUS.TO_BE_EXECUTED:
            console.printout('You must resume SessionID:', args.SESSION_ID)
            sys.exit(1)

        if status_code == stc.STC_SESSION_STATUS.MANUAL_ACTIVITIES_REQUIRED:
            console.printout('You must manually configured SessionID:', args.SESSION_ID)

            _print_session_current_task_logs(console, conn, args.SESSION_ID, task)

            sys.exit(1)

        if status_code == stc.STC_SESSION_STATUS.STOPPED:
            console.printout('Stopped SessionID:', args.SESSION_ID)

            _print_session_current_task_logs(console, conn, args.SESSION_ID, task)

            sys.exit(1)

        if status_code == stc.STC_SESSION_STATUS.ABORTED:
            console.printout('Aborted SessionID:', args.SESSION_ID)
            sys.exit(1)

        if status_code == stc.STC_SESSION_STATUS.ERRORS_OCCURRED:
            console.printout('Errored SessionID:', args.SESSION_ID)

            _print_session_current_task_logs(console, conn, args.SESSION_ID, task)

            if not args.skip_tasks:
                sys.exit(1)

            if not _do_skip_task(console, conn, args.SESSION_ID, task['TASKNAME'], task['LNR']):
                sys.exit(1)

            _do_session_resume(conn, args.SESSION_ID)
            # Beware: this code branch does not exit!!!

        time.sleep(5)

    return 0


@SessionGroup.argument('SESSION_ID', type=str, help='Session ID')
@SessionGroup.command('logs')
def session_logs(connection, args):
    """Fetches and prints out session logs"""

    console = sap.cli.core.get_console()
    console.printout(stc.tm_session_get_log(conn, args.SESSION_ID))

    return 0


@SessionGroup.argument('SESSION_ID', type=str, help='Session ID')
@SessionGroup.command('parameters')
def session_parameters_get(connection, args):
    """Get Session parameters"""

    console = sap.cli.core.get_console()

    ret = stc.tm_session_get_parameters(conn, args.SESSION_ID)
    for param in ret['ET_PARAMETER']:
        console.printout('{TASKNAME}:{LNR}: {FIELDNAME}={VALUE}'.format(**param))

    return 0


def _get_tasks_from_args(connection, args):
    if args.task_name == '*':
        return [(task['TASKNAME'], task['LNR']) for task in stc.get_session_tasks(conn, args.SESSION_ID)]

    task_lnr = args.task_lnr

    if task_lnr is None:
        task_lnr = stc.get_session_task_lnr(conn, args.SESSION_ID, args.task_name)

    return [(args.task_name, task_lnr)]


@TaskGroup.command('skip')
def task_skip(connection, args):
    """Skip the task in the session"""

    console = sap.cli.core.get_console()
    tasks = _get_tasks_from_args(connection, args)

    for task, lnr in tasks:
        _do_skip_task(console, conn, args.SESSION_ID, task, lnr)

    return 0


@TaskGroup.command('unskip')
def task_unskip(connection, args):
    """Mark the task for execution in the session"""

    console = sap.cli.core.get_console()

    tasks = _get_tasks_from_args(connection, args)

    for task, lnr in tasks:
        console.printout('Un-skipping: {}:{}'.format(task, lnr))
        ret = stc.tm_task_unskip(conn, args.SESSION_ID, task, lnr)

        if ret['E_UNSKIPPED'] == '':
            console.printout(ret['ET_RETURN'][0]['MESSAGE'])

    return 0


@TaskGroup.argument('VALUE')
@TaskGroup.argument('FIELDNAME')
@TaskGroup.command('set-parameter')
def task_parameter_set(connection, args):
    """Set the task parameter value"""

    task_lnr = args.task_lnr

    if task_lnr is None:
        task_lnr = stc.get_session_task_lnr(conn, args.session_id, args.task_name)

    stc.tm_task_set_parameter(conn, args.SESSION_ID, args.task_name, task_lnr, [stc.build_task_parameter(args.FIELDNAME, args.VALUE)])

    return 0
