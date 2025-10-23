"""gCTS task methods"""


import sap.cli.core
import sap.cli.helpers


from sap.rest.gcts.repo_task import (
    RepositoryTask,
)
from sap.rest.gcts.errors import (
    GCTSRequestError,
    SAPCliError,
    GCTSRepoNotExistsError,
    GCTSRepoCloneError,
)


from sap.cli.gcts import CommandGroup


@CommandGroup.argument('--tid', type=str)
@CommandGroup.argument('package')  # rid url
@CommandGroup.command()
def task_info(connection, args):
    """Get task information"""

    console = sap.cli.core.get_console()

    # Validate parameters
    if not args.tid or not args.tid.strip():
        console.printerr('Task ID (--tid) is required and cannot be empty')
        return 1

    if not args.package or not args.package.strip():
        console.printerr('Package name is required and cannot be empty')
        return 1

    task = RepositoryTask(connection, args.package)

    try:
        task = task.get_by_id(args.tid)
    except GCTSRequestError as exc:
        console.printerr(f'Task retrieval failed: {exc}')
        return 1

    console.printout('Task ID:', task.tid)
    console.printout('Task Status:', task.status)
    console.printout('Task Type:', task.type)

    return 0


@CommandGroup.argument('package')  # rid url
@CommandGroup.command()
def tasks_list(connection, args):
    """Get task information"""

    console = sap.cli.core.get_console()

    if not args.package or not args.package.strip():
        console.printerr('Package name is required and cannot be empty')
        return 1

    try:
        tasks = RepositoryTask(connection, args.package).get_list()
    except GCTSRequestError as exc:
        console.printerr(f'Tasks retrieval failed: {exc}')
        return 1
    columns = (
        sap.cli.helpers.TableWriter.Columns()
        ('tid', 'Task ID')
        ('status', 'Status')
        ('type', 'Type')
        .done()
    )
    sap.cli.helpers.TableWriter(tasks, columns).printout(console)

    return 0


@CommandGroup.argument('--branch', type=str, default=None)
@CommandGroup.argument('package')
@CommandGroup.command()
def create_clone_task(connection, args):
    """Get task information"""

    console = sap.cli.core.get_console()
    try:
        task = RepositoryTask(connection, args.package).create(RepositoryTask.TaskDefinition.CLONE_REPOSITORY, args.branch).schedule_task()

    except GCTSRepoNotExistsError as exc:
        console.printerr(f'Repository does not exist: {exc}')
        return 1
    except GCTSRepoCloneError as exc:
        console.printerr(f'Repository cannot be cloned: {exc}')
        return 1
    except GCTSRequestError as exc:
        console.printerr(f'Task creation or scheduling failed: {exc}')
        return 1
    except SAPCliError as exc:
        console.printerr(f'Task creation failed: {exc}')
        return 1

    console.printout('Task ID:', task.tid)
    console.printout('Task Status:', task.status)
    console.printout('Task Type:', task.type)
    return 0


@CommandGroup.argument('--tid', type=str)
@CommandGroup.argument('package')
@CommandGroup.command()
def delete_task(connection, args):
    """Delete a task"""

    console = sap.cli.core.get_console()
    try:
        RepositoryTask(connection, args.package, data={'tid': args.tid}).delete()
    except GCTSRepoNotExistsError as exc:
        console.printerr(f'Repository does not exist: {exc}')
        return 1
    except GCTSRequestError as exc:
        console.printerr(f'Task delete request failed: {exc}')
        return 1

    console.printout('Task deleted successfully')
    return 0
