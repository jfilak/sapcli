"""Simple API for gCTS operations"""

import json
import time

from sap.cli.core import get_console
from sap import get_logger
from sap.rest.errors import HTTPRequestError
from sap.rest.gcts.remote_repo import (
    Repository,
)
from sap.rest.gcts.repo_task import RepositoryTask
from sap.rest.gcts.errors import (
    exception_from_http_error,
    GCTSRepoAlreadyExistsError,
    SAPCliError,
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


def wait_for_task_execution(repo, task_id, wait_for_ready, pull_period):
    """Wait for task execution to finish"""
    console = get_console()
    start_time = time.time()
    while time.time() - start_time < wait_for_ready:
        try:
            task = repo.get_task_by_id(task_id)
            filtered_task_info = {
                'tid': task.tid,
                'rid': task.rid,
                'type': task.type,
                'status': task.status
            }
            console.printout('\n', 'Task monitoring:', json.dumps(filtered_task_info, indent=4))
            if task.status == RepositoryTask.TaskStatus.FINISHED.value:
                return task

            if task.status == RepositoryTask.TaskStatus.ABORTED.value:
                raise SAPCliError(f'Task execution aborted: task {task_id} for repository {repo.rid}')

        except HTTPRequestError:
            _mod_log().debug(f'Failed to get status of the task {task_id} for repository {repo.rid}')
        time.sleep(pull_period)
    raise SAPCliError(f'Waiting for the task execution timed out: task {task_id} for repository {repo.rid}. You can check the task status manually with the command "gcts task_info --tid {task_id} {repo.rid} "')


# pylint: disable=too-many-arguments
def clone(repo: Repository):
    """Clones the repository in the target systems"""

    if not repo.is_cloned:
        repo.clone()
    else:
        _mod_log().info('Not cloning the repository "%s": already performed or repository is not created.')

    return repo


def schedule_clone(repo, connection, branch=None):
    """Schedule a repository cloning task on the target systems"""
    task = None
    if not repo.is_cloned:
        task = RepositoryTask(connection, repo.rid).create(RepositoryTask.TaskDefinition.CLONE_REPOSITORY, parameters=RepositoryTask.TaskParameters(branch=branch)).schedule_task()
    else:
        _mod_log().info('Repository "%s" cloning not scheduled: already performed or repository is not created.')

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
        # Fetch repository data to ensure it exists
        _ = repo.status

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
