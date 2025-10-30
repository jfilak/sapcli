"""gCTS task methods"""


import sap.cli.core
import sap.cli.helpers


from sap.rest.gcts.repo_task import (
    RepositoryTask,
)
from sap.rest.gcts.errors import (
    GCTSRequestError,
    GCTSRepoNotExistsError,
)
from sap.cli.gcts_utils import gcts_exception_handler


class CommandGroup(sap.cli.core.CommandGroup):
    """Adapter converting command line parameters to sap.rest.gcts
       methods calls.
    """
    commands_wrapper = gcts_exception_handler

    def __init__(self):
        super().__init__('task')


@CommandGroup.argument('--tid', type=str)
@CommandGroup.argument('package')
@CommandGroup.command('info')
def info(connection, args):
    """Get task information"""
    console = sap.cli.core.get_console()

    if not args.tid or not args.tid.strip() or not args.package or not args.package.strip():
        console.printerr('Invalid command line options\nRun: sapcli gcts_task info --help')
        return 1

    try:
        task = RepositoryTask(connection, args.package).get_by_id(args.tid)
        console.printout('Task ID:', task.tid)
        console.printout('Task Status:', task.status)
        console.printout('Task Type:', task.type)

        return 0
    except GCTSRequestError as exc:
        console.printerr(f'Task retrieval failed: {exc}')
        return 1


@CommandGroup.argument('package')  # rid
@CommandGroup.command('print-list')
def print_list(connection, args):
    """Get task information"""

    console = sap.cli.core.get_console()

    if not args.package or not args.package.strip():
        console.printerr('Invalid command line options\nRun: sapcli gcts_task print_list --help')
        return 1

    try:
        tasks = RepositoryTask(connection, args.package).get_list()
        if tasks and len(tasks) > 0:
            columns = (
                sap.cli.helpers.TableWriter.Columns()
                ('tid', 'Task ID')
                ('status', 'Status')
                ('type', 'Type')
                .done()
            )
            sap.cli.helpers.TableWriter(tasks, columns).printout(console)
        else:
            console.printout(f'No tasks found for repository: {args.package}')
    except GCTSRequestError as exc:
        console.printerr(f'Tasks retrieval failed for repository: {args.package}: {exc}')
        return 1

    return 0


@CommandGroup.argument('--tid', type=str)
@CommandGroup.argument('package')
@CommandGroup.command('delete')
def delete(connection, args):
    """Delete a task"""

    console = sap.cli.core.get_console()
    try:
        RepositoryTask(connection, args.package, data={'tid': args.tid}).delete()
    except GCTSRepoNotExistsError as exc:
        console.printerr(f'Repository {args.package} does not exist: {exc}')
        return 1
    except GCTSRequestError as exc:
        console.printerr(f'Task delete request failed: {exc}')
        return 1

    console.printout('Task deleted successfully')
    return 0
