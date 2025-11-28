"""Simple API for gCTS operations"""

import json
import time
from typing import Optional

from sap import get_logger
from sap.errors import OperationTimeoutError
from sap.rest.errors import HTTPRequestError
from sap.rest.gcts.remote_repo import Repository
from sap.rest.gcts.repo_task import RepositoryTask
from sap.rest.gcts.errors import (
    exception_from_http_error,
    GCTSRepoAlreadyExistsError,
    SAPCliError,
)
from sap.rest.gcts.sugar import (
    context_stub,
    abap_modifications_disabled,
    abap_modifications_added_only_to_buffer,
    SugarOperationProgress,
    LogTaskOperationProgress,
)


def _mod_log():
    return get_logger()


def fetch_repos(connection):
    """Returns list of repositories in the target systems defined by the given
       connection.
    """

    try:
        response = connection.get_json('repository')
    except HTTPRequestError as ex:
        raise exception_from_http_error(ex) from ex

    result = response.get('result', [])
    return [Repository(connection, repo['rid'], data=repo) for repo in result]


def wait_for_operation(repo, condition_fn, wait_for_ready, http_exc):
    """Wait for operation to finish"""

    start_time = time.time()
    while time.time() - start_time < wait_for_ready:
        repo.wipe_data()
        try:
            if condition_fn(repo):
                return

        except HTTPRequestError:
            _mod_log().debug('Failed to get status of the repository %s', repo.rid)

    raise SAPCliError(f'Waiting for the operation timed out\n{http_exc}')


def wait_for_task_execution(task: RepositoryTask, wait_for_ready, poll_period=30, poll_cb=None):
    """Wait for task execution to finish"""
    start_time = time.time()

    while time.time() - start_time < wait_for_ready:
        try:
            task.get_by_id(task.tid)
            if callable(poll_cb):
                poll_cb(None, task.to_dict())
            if task.status == RepositoryTask.TaskStatus.FINISHED.value:
                return task
            if task.status == RepositoryTask.TaskStatus.ABORTED.value:
                raise SAPCliError(f'Task execution aborted: task {task.tid} for repository {task.rid}.')
        except HTTPRequestError as ex:
            if callable(poll_cb):
                poll_cb(f'Failed to get status of the task {task.tid}: {str(ex)}', None)
        time.sleep(poll_period)

    raise OperationTimeoutError(f'Waiting for the task execution timed out: task {task.tid} for repository {task.rid}.')


def clone(connection, url, rid, vsid='6IT', start_dir='src/', vcs_token=None,
          error_exists=True, role='SOURCE', typ='GITHUB', no_import=False,
          buffer_only=False, progress_consumer: Optional[SugarOperationProgress] = None) -> Repository:
    """Creates and clones the repository in the target systems"""

    repo = create(
        connection=connection,
        url=url,
        rid=rid,
        vsid=vsid,
        start_dir=start_dir,
        vcs_token=vcs_token,
        error_exists=error_exists,
        role=role,
        typ=typ,
    )

    if repo.is_cloned:
        _mod_log().info('Not cloning the repository "%s": already performed', repo.rid)
        return repo
    with (
        abap_modifications_disabled(repo, progress_consumer) if no_import else context_stub(),
        abap_modifications_added_only_to_buffer(repo, progress_consumer) if buffer_only else context_stub()
    ):
        repo.clone()
    return repo


# pylint: disable=too-many-locals
def clone_with_task(connection, url, rid, vsid='6IT', start_dir='src/', vcs_token=None,
                    error_exists=True, role='SOURCE', typ='GITHUB', no_import=False,
                    buffer_only=False, wait_for_ready: int = 600, poll_period: int = 30,
                    progress_consumer: LogTaskOperationProgress | None = None) -> Repository:
    """Creates and clones the repository in the target systems and schedules a cloning task"""

    repo = create(
        connection=connection,
        url=url,
        rid=rid,
        vsid=vsid,
        start_dir=start_dir,
        vcs_token=vcs_token,
        error_exists=error_exists,
        role=role,
        typ=typ,
    )
    if progress_consumer:
        progress_consumer.progress_message(f'Repository "{repo.rid}" has been created.')

    if repo.is_cloned:
        if progress_consumer:
            progress_consumer.progress_message(f'Not cloning the repository "{repo.rid}": already performed.')
        return repo
    with (
        abap_modifications_disabled(repo, progress_consumer) if no_import else context_stub(),
        abap_modifications_added_only_to_buffer(repo, progress_consumer) if buffer_only else context_stub()
    ):

        task = schedule_clone(connection, repo)

        if not task:
            return repo
        if progress_consumer:
            progress_consumer.progress_message(f'CLONE task "{task.tid}" has been scheduled.')
        if wait_for_ready > 0:
            def _poll_cb(error_msg, task):
                if error_msg and progress_consumer:
                    progress_consumer.update_task(error_msg, None)
                if task and progress_consumer:
                    progress_consumer.update_task(None, task)

            wait_for_task_execution(task, wait_for_ready, poll_period, _poll_cb)
            if progress_consumer:
                progress_consumer.progress_message(f'CLONE task "{task.tid}" has finished successfully.')
        else:
            raise OperationTimeoutError

    repo.refresh()

    return repo


def schedule_clone(connection, repo, branch=None) -> Optional[RepositoryTask]:
    """Schedule a repository cloning task on the target systems"""
    if repo.is_cloned:
        _mod_log().info('Repository "%s" cloning not scheduled: already performed or repository is not created.', repo.rid)
        return None

    task_parameters = RepositoryTask.TaskParameters(branch=branch)
    task = RepositoryTask(connection, repo.rid)
    task = task.create(
        RepositoryTask.TaskDefinition.CLONE_REPOSITORY,
        parameters=task_parameters)
    task.schedule_task()
    return task


def create(connection, url, rid, vsid='6IT', start_dir='src/', vcs_token=None, error_exists=True,
           role='SOURCE', typ='GITHUB'):
    """Creates the repository in the target systems"""

    config = {}

    if start_dir:
        config['VCS_TARGET_DIR'] = start_dir

    if vcs_token:
        config['CLIENT_VCS_AUTH_TOKEN'] = vcs_token

    repo = Repository(connection, rid)

    try:
        repo.create(url, vsid, config=config, role=role, typ=typ)
    except GCTSRepoAlreadyExistsError as ex:
        if error_exists:
            raise ex

        _mod_log().debug(ex)
        _mod_log().info(str(ex))

        repo.wipe_data()

    return repo


def checkout(connection, branch, rid=None, repo=None):
    """Checks out the given branch in the given repository on the give system"""

    if repo is None:
        repo = Repository(connection, rid)

    return repo.checkout(branch)


def log(connection, rid=None, repo=None):
    """Returns log history of the given repository on the give system"""

    if repo is None:
        repo = Repository(connection, rid)

    return repo.log()


def pull(connection, rid=None, repo=None):
    """Pulls the given repository on the give system"""

    if repo is None:
        repo = Repository(connection, rid)

    return repo.pull()


def delete(connection, rid=None, repo=None):
    """Deletes the given repository on the give system"""

    if repo is None:
        repo = Repository(connection, rid)

    return repo.delete()


def get_user_credentials(connection):
    """Get Token for the currently logged in user"""

    response = connection.get_json('user')
    user_data = response.get('user', None)
    if user_data is None:
        raise SAPCliError('gCTS response does not contain \'user\'')

    config_data = user_data.get('config', None)
    if config_data is None:
        return []

    user_credentials = [cred for cred in config_data if cred['key'] == 'USER_AUTH_CRED_ENDPOINTS']
    return json.loads(user_credentials[0]['value'])


def set_user_api_token(connection, api_url, token):
    """Set Token for the currently logged in user"""

    body = {
        'endpoint': api_url,
        'user': '',
        'password': '',
        'token': token,
        'type': 'token'
    }

    connection.post_obj_as_json('user/credentials', body)


def delete_user_credentials(connection, api_url):
    """Delete Token for the currently logged in user"""

    body = {
        'endpoint': api_url,
        'user': '',
        'password': '',
        'token': '',
        'type': 'none'
    }

    connection.post_obj_as_json('user/credentials', body)


def get_system_config_property(connection, config_key):
    """Get configuration property value for given key"""

    response = connection.get_json(f'system/config/{config_key}')
    config_value = response.get('result')
    if config_value is None:
        raise SAPCliError("gCTS response does not contain 'result'")

    return config_value


def list_system_config(connection):
    """List system configuration"""

    response = connection.get_json('system')
    system = response.get('result')
    if system is None:
        raise SAPCliError("gCTS response does not contain 'result'")

    return system.get('config', [])


def set_system_config_property(connection, config_key, value):
    """Create or update the configuration property"""

    body = {
        'key': config_key,
        'value': value,
    }
    response = connection.post_obj_as_json('system/config', body).json()
    config_value = response.get('result')
    if config_value is None:
        raise SAPCliError("gCTS response does not contain 'result'")

    return config_value


def delete_system_config_property(connection, config_key):
    """Delete configuration property"""

    return connection.delete_json(f'system/config/{config_key}')
